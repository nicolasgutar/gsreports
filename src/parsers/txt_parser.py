"""
Parser functions for PILA planilla .txt files.
Supports 4 types of parsing:
- tipo1: Extract header/encabezado information
- tipo2: Extract detail/detalle records
- tipo3: Extract totals (renglones 31, 36, 39)
- tipo4: Extract additional data
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional


def parsear_tipo1(contenido: str) -> pd.DataFrame:
    """
    Parse tipo1 - Encabezado (header) information.
    Extracts general planilla information like NIT, periodo, etc.
    
    Args:
        contenido: String content of the .txt file
        
    Returns:
        DataFrame with header information
    """
    encabezado_data = {
        'nit_aportante': None,
        'razon_social': None,
        'periodo_pago': None,
        'fecha_pago': None,
        'numero_planilla': None,
        'tipo_planilla': None,
        'numero_registros': 0
    }
    
    # Parse header lines - assuming specific format
    lines = contenido.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Extract NIT (formato: NIT followed by digits)
        nit_match = re.search(r'NIT[:\s]*(\d+)', line, re.IGNORECASE)
        if nit_match:
            encabezado_data['nit_aportante'] = nit_match.group(1)
        
        # Extract period (formato: periodo AAAA-MM or similar)
        periodo_match = re.search(r'PERIODO[:\s]*(\d{4}-\d{2})', line, re.IGNORECASE)
        if periodo_match:
            encabezado_data['periodo_pago'] = periodo_match.group(1)
        
        # Extract planilla number
        planilla_match = re.search(r'PLANILLA[:\s]*(\w+)', line, re.IGNORECASE)
        if planilla_match:
            encabezado_data['numero_planilla'] = planilla_match.group(1)
    
    return pd.DataFrame([encabezado_data])


def parsear_tipo2(contenido: str) -> pd.DataFrame:
    """
    Parse tipo2 - Detalles (detail records).
    Extracts individual employee/contributor records.
    
    Args:
        contenido: String content of the .txt file
        
    Returns:
        DataFrame with detail records
    """
    detalles = []
    lines = contenido.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Parse detail lines - assuming tab or pipe-separated format
        # Format example: tipo_documento|num_documento|nombre|salario|dias|...
        parts = re.split(r'[\t|]', line)
        
        if len(parts) >= 5:
            detalle = {
                'tipo_documento': parts[0] if len(parts) > 0 else None,
                'numero_documento': parts[1] if len(parts) > 1 else None,
                'nombre_completo': parts[2] if len(parts) > 2 else None,
                'salario_base': float(parts[3]) if len(parts) > 3 and parts[3].replace('.', '').isdigit() else 0.0,
                'dias_cotizados': int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
            }
            detalles.append(detalle)
    
    return pd.DataFrame(detalles)


def parsear_tipo3(contenido: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Parse tipo3 - Renglones de totales (31, 36, 39).
    Extracts total values from specific accounting lines.
    
    Args:
        contenido: String content of the .txt file
        
    Returns:
        Tuple of three DataFrames: (renglon_31_aportes, renglon_36_mora, renglon_39_total)
        Each DataFrame contains ALL available fields parsed from the corresponding line.
    """
    # Initialize data structures with ALL possible fields
    renglon_31_data = {
        'renglon': 31,
        'descripcion': 'Aportes',
        'valor_total': 0.0,
        'valor_salud': 0.0,
        'valor_pension': 0.0,
        'valor_riesgos': 0.0,
        'valor_caja': 0.0,
        'valor_sena': 0.0,
        'valor_icbf': 0.0,
        'valor_subsistencia': 0.0,
        'numero_cotizantes': 0,
        'dias_cotizados': 0,
        'ibc_total': 0.0,
        'observaciones': None
    }
    
    renglon_36_data = {
        'renglon': 36,
        'descripcion': 'Intereses de Mora',
        'valor_total': 0.0,
        'valor_mora_salud': 0.0,
        'valor_mora_pension': 0.0,
        'valor_mora_riesgos': 0.0,
        'valor_mora_caja': 0.0,
        'tasa_interes': 0.0,
        'dias_mora': 0,
        'fecha_limite_pago': None,
        'observaciones': None
    }
    
    renglon_39_data = {
        'renglon': 39,
        'descripcion': 'Total a Pagar',
        'valor_total': 0.0,
        'valor_aportes': 0.0,
        'valor_mora': 0.0,
        'valor_otros': 0.0,
        'descuentos': 0.0,
        'neto_pagar': 0.0,
        'forma_pago': None,
        'numero_autorizacion': None,
        'fecha_transaccion': None,
        'observaciones': None
    }
    
    lines = contenido.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Parse Renglon 31 - Aportes
        if re.search(r'R(?:ENGLON)?[\s]*31', line, re.IGNORECASE) or ('APORTES' in line.upper() and 'RENGLON' in line.upper()):
            # Extract all numeric values from the line
            valores = re.findall(r'\d+\.?\d*', line)
            if valores:
                valores_float = [float(v) for v in valores]
                # Skip the renglon number (31) and get actual values
                valores_float = [v for v in valores_float if v != 31]
                # Map values to fields (adjust indices based on actual format)
                if len(valores_float) >= 1:
                    renglon_31_data['valor_total'] = valores_float[0]
                if len(valores_float) >= 2:
                    renglon_31_data['valor_salud'] = valores_float[1]
                if len(valores_float) >= 3:
                    renglon_31_data['valor_pension'] = valores_float[2]
                if len(valores_float) >= 4:
                    renglon_31_data['valor_riesgos'] = valores_float[3]
                if len(valores_float) >= 5:
                    renglon_31_data['valor_caja'] = valores_float[4]
                if len(valores_float) >= 6:
                    renglon_31_data['valor_sena'] = valores_float[5]
                if len(valores_float) >= 7:
                    renglon_31_data['valor_icbf'] = valores_float[6]
        
        # Parse Renglon 36 - Mora
        elif re.search(r'R(?:ENGLON)?[\s]*36', line, re.IGNORECASE) or ('MORA' in line.upper() and 'RENGLON' in line.upper()):
            valores = re.findall(r'\d+\.?\d*', line)
            if valores:
                valores_float = [float(v) for v in valores]
                # Skip the renglon number (36) and get actual values
                valores_float = [v for v in valores_float if v != 36]
                if len(valores_float) >= 1:
                    renglon_36_data['valor_total'] = valores_float[0]
                if len(valores_float) >= 2:
                    renglon_36_data['valor_mora_salud'] = valores_float[1]
                if len(valores_float) >= 3:
                    renglon_36_data['valor_mora_pension'] = valores_float[2]
                if len(valores_float) >= 4:
                    renglon_36_data['valor_mora_riesgos'] = valores_float[3]
        
        # Parse Renglon 39 - Total
        elif re.search(r'R(?:ENGLON)?[\s]*39', line, re.IGNORECASE) or ('TOTAL' in line.upper() and 'RENGLON' in line.upper()):
            valores = re.findall(r'\d+\.?\d*', line)
            if valores:
                valores_float = [float(v) for v in valores]
                # Skip the renglon number (39) and get actual values
                valores_float = [v for v in valores_float if v != 39]
                if len(valores_float) >= 1:
                    renglon_39_data['valor_total'] = valores_float[0]
                if len(valores_float) >= 2:
                    renglon_39_data['valor_aportes'] = valores_float[1]
                if len(valores_float) >= 3:
                    renglon_39_data['valor_mora'] = valores_float[2]
                if len(valores_float) >= 4:
                    renglon_39_data['neto_pagar'] = valores_float[3]
    
    # Create DataFrames with ALL fields
    df_r31 = pd.DataFrame([renglon_31_data])
    df_r36 = pd.DataFrame([renglon_36_data])
    df_r39 = pd.DataFrame([renglon_39_data])
    
    return df_r31, df_r36, df_r39


def parsear_tipo4(contenido: str) -> pd.DataFrame:
    """
    Parse tipo4 - Datos adicionales (additional data).
    Extracts any additional information not covered by other parsers.
    
    Args:
        contenido: String content of the .txt file
        
    Returns:
        DataFrame with additional data
    """
    datos_adicionales = {
        'entidad_receptora': None,
        'codigo_entidad': None,
        'direccion': None,
        'telefono': None,
        'email': None,
        'observaciones_generales': None,
        'estado_planilla': None,
        'fecha_generacion': None
    }
    
    lines = contenido.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
        if email_match:
            datos_adicionales['email'] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'TEL[EFONO]*[:\s]*(\d{7,10})', line, re.IGNORECASE)
        if phone_match:
            datos_adicionales['telefono'] = phone_match.group(1)
        
        # Extract entity code
        codigo_match = re.search(r'CODIGO[:\s]*(\w+)', line, re.IGNORECASE)
        if codigo_match:
            datos_adicionales['codigo_entidad'] = codigo_match.group(1)
    
    return pd.DataFrame([datos_adicionales])
