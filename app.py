# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
from typing import Optional
import traceback

from fastapi.responses import RedirectResponse
# Importar funciones de los módulos existentes
from config import Config
from db_connector import DatabaseConnector
from db_queries import get_user_transactions, get_transactions_grouped_by_category
from balance_sheet_queries import get_all_balance_sheet_data
from transaction_processor import (
    create_transactions_dataframe,
    process_grouped_data_for_pnl
)
from pnl import generate_pnl_report, generate_pnl_report_by_account
from balance_sheet import generate_balance_sheet
from main import create_reports_in_google_sheets

app = FastAPI(title="Financial Reports API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    userId: str

class ReportResponse(BaseModel):
    success: bool
    message: str
    sheet_url: Optional[str] = None
    error: Optional[str] = None

@app.post("/reports")
async def generate_reports(request: ReportRequest):
    """
    Genera reportes financieros para un usuario específico.

    Args:
        request: Objeto con el userId para generar los reportes

    Returns:
        ReportResponse con el resultado de la operación
    """
    user_id = request.userId.strip()

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID no puede estar vacío")

    # Inicializar variables
    db = None

    try:
        print(f"Generando reportes financieros para el usuario: {user_id}")

        # Validar configuración
        if not Config.validate():
            raise Exception("Validación de configuración falló")

        # Conectar a la base de datos
        print("--- Conectando a la base de datos ---")
        db = DatabaseConnector(**Config.get_db_config())

        # Obtener transacciones
        print(f"Obteniendo transacciones para el usuario {user_id}...")
        start_date = Config.REPORT_START_DATE
        end_date = Config.REPORT_END_DATE

        transactions = get_user_transactions(
            db, user_id,
            start_date=start_date,
            end_date=end_date,
            limit=Config.DEFAULT_TRANSACTION_LIMIT
        )

        print(f"✓ Obtenidas {len(transactions)} transacciones")

        if not transactions:
            print("⚠ ADVERTENCIA: No se encontraron transacciones para este usuario.")

        # Crear DataFrame de transacciones para la hoja
        transactions_df = create_transactions_dataframe(transactions)

        # Procesar transacciones usando consulta agrupada para P&L
        print("\nProcesando transacciones para P&L usando consulta agrupada...")
        grouped_data = get_transactions_grouped_by_category(
            db, user_id,
            start_date=start_date,
            end_date=end_date
        )

        # Procesar los datos agrupados en formato P&L
        data = process_grouped_data_for_pnl(grouped_data)
        print(f"✓ Datos P&L calculados. Ingreso neto: ${data['Net Income']:,.2f}")

        # Obtener datos del Balance Sheet desde la base de datos
        print("\nObteniendo datos del Balance Sheet desde la base de datos...")
        balance_sheet_data = get_all_balance_sheet_data(
            db, user_id,
            start_date=start_date,
            end_date=end_date
        )

        # Combinar datos del balance sheet con datos P&L
        data.update(balance_sheet_data)
        print("✓ Datos del Balance Sheet cargados desde la base de datos")

        # Generar reporte P&L (General)
        print("\n--- Generando Reportes ---")
        pnl_df, net_income, pnl_formatting_rows = generate_pnl_report(data, user_id)
        if pnl_df is None:
            raise Exception("Error generando reporte P&L general")

        # Generar reporte P&L Personal
        print("\n--- Generando Reporte P&L Personal ---")
        personal_grouped_data = get_transactions_grouped_by_category(
            db, user_id,
            start_date=start_date,
            end_date=end_date,
            account_category="personal"
        )
        personal_data = process_grouped_data_for_pnl(personal_grouped_data)
        personal_pnl_df, personal_net_income, _ = generate_pnl_report_by_account(personal_data, user_id, "Personal")
        print(f"✓ Datos P&L Personal calculados. Ingreso neto: ${personal_net_income:,.2f}")

        # Generar reporte P&L de Negocio
        print("\n--- Generando Reporte P&L de Negocio ---")
        business_grouped_data = get_transactions_grouped_by_category(
            db, user_id,
            start_date=start_date,
            end_date=end_date,
            account_category="business"
        )
        business_data = process_grouped_data_for_pnl(business_grouped_data)
        business_pnl_df, business_net_income, _ = generate_pnl_report_by_account(business_data, user_id, "Business")
        print(f"✓ Datos P&L de Negocio calculados. Ingreso neto: ${business_net_income:,.2f}")

        # Generar Balance Sheet (pasando el net_income calculado del P&L general)
        balance_sheet_df = generate_balance_sheet(data, user_id, net_income)

        # Crear y escribir en nuevo documento de Google Sheets
        sheet_link = create_reports_in_google_sheets(
            user_id, pnl_df, balance_sheet_df, transactions_df, pnl_formatting_rows,
            personal_pnl_df, business_pnl_df
        )

        print(f"\n✅ Reportes financieros generados exitosamente!")
        return {
            "success": True,
            "redirectUrl": sheet_link,
            "message": "Reports generated successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating reports: {str(e)}")

    finally:
        # Limpiar conexión a la base de datos
        if db:
            db.close_all_connections()
            print("\n✓ Conexiones de base de datos cerradas")

@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {"message": "Financial Reports API está funcionando"}

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud."""
    return {"status": "healthy", "service": "Financial Reports API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)