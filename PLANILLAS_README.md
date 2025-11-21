# PILA Planillas Parser and Log Matching System

## Overview

This system parses PILA (Planilla Integrada de Liquidación de Aportes) planilla .txt files and matches them with financial log entries from Excel files. It supports comprehensive data extraction using four different parser types.

## Directory Structure

```
gsreports/
├── notebooks/
│   └── BuscandoEnLog.ipynb          # Main notebook for parsing and matching
├── src/
│   └── parsers/
│       └── txt_parser.py            # Parser functions for planilla files
└── Planillas/
    ├── *.txt                        # Planilla text files
    └── LOG FINANCIERO FPOB OCTUBRE .xlsx  # Excel log file
```

## Parser Types

### Parser Tipo1 - Encabezados (Headers)
Extracts general planilla information:
- `nit_aportante`: Company NIT number
- `razon_social`: Company legal name
- `periodo_pago`: Payment period (YYYY-MM)
- `fecha_pago`: Payment date
- `numero_planilla`: Planilla number
- `tipo_planilla`: Planilla type
- `numero_registros`: Number of records

### Parser Tipo2 - Detalles (Details)
Extracts individual employee/contributor records:
- `tipo_documento`: Document type (CC, CE, etc.)
- `numero_documento`: Document number
- `nombre_completo`: Full name
- `salario_base`: Base salary
- `dias_cotizados`: Days contributed

### Parser Tipo3 - Renglones de Totales (Total Lines)
Extracts comprehensive total values from accounting lines. **All available fields are displayed**.

#### Renglon 31 - Aportes (Contributions) - 14 fields:
- `renglon`: Line number (31)
- `descripcion`: Description
- `valor_total`: Total value
- `valor_salud`: Health contribution
- `valor_pension`: Pension contribution
- `valor_riesgos`: Occupational risks contribution
- `valor_caja`: Family compensation fund
- `valor_sena`: SENA contribution
- `valor_icbf`: ICBF contribution
- `valor_subsistencia`: Subsistence value
- `numero_cotizantes`: Number of contributors
- `dias_cotizados`: Days contributed
- `ibc_total`: Total contribution base income
- `observaciones`: Observations

#### Renglon 36 - Intereses de Mora (Late Payment Interest) - 11 fields:
- `renglon`: Line number (36)
- `descripcion`: Description
- `valor_total`: Total interest
- `valor_mora_salud`: Health late payment interest
- `valor_mora_pension`: Pension late payment interest
- `valor_mora_riesgos`: Occupational risks late payment interest
- `valor_mora_caja`: Family compensation fund late payment interest
- `tasa_interes`: Interest rate
- `dias_mora`: Days late
- `fecha_limite_pago`: Payment deadline
- `observaciones`: Observations

#### Renglon 39 - Total a Pagar (Total to Pay) - 12 fields:
- `renglon`: Line number (39)
- `descripcion`: Description
- `valor_total`: Total value
- `valor_aportes`: Contributions value
- `valor_mora`: Late payment interest value
- `valor_otros`: Other values
- `descuentos`: Discounts
- `neto_pagar`: Net amount to pay
- `forma_pago`: Payment method
- `numero_autorizacion`: Authorization number
- `fecha_transaccion`: Transaction date
- `observaciones`: Observations

### Parser Tipo4 - Datos Adicionales (Additional Data)
Extracts supplementary information:
- `entidad_receptora`: Receiving entity
- `codigo_entidad`: Entity code
- `direccion`: Address
- `telefono`: Phone number
- `email`: Email address
- `observaciones_generales`: General observations
- `estado_planilla`: Planilla status
- `fecha_generacion`: Generation date

## Matching Logic

The system uses a **2-criteria intersection approach** where BOTH criteria must be met simultaneously:

1. **NIT Match**: Exact NIT match in any text column of the Excel log
2. **Value Match**: Monetary value within ±5% tolerance in any numeric column

A match is only reported when a row in the Excel log satisfies BOTH criteria.

## Usage

### Basic Usage in Jupyter Notebook

```python
# Import parsers
from src.parsers.txt_parser import parsear_tipo1, parsear_tipo2, parsear_tipo3, parsear_tipo4

# Read planilla file
with open('Planillas/planilla_001.txt', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Parse using tipo3 to get all renglon data
df_r31, df_r36, df_r39 = parsear_tipo3(contenido)

# Display all fields
print(f"Renglon 31 has {len(df_r31.columns)} fields:")
display(df_r31)

print(f"Renglon 36 has {len(df_r36.columns)} fields:")
display(df_r36)

print(f"Renglon 39 has {len(df_r39.columns)} fields:")
display(df_r39)
```

### Complete Workflow

Open `notebooks/BuscandoEnLog.ipynb` and run all cells to:

1. **Process all planillas**: Parse all .txt files in `/Planillas` directory
2. **Analyze Excel log**: Load and analyze the financial log file
3. **Match planillas with log**: Find matching transactions using NIT + value criteria
4. **Display results**: Show detailed statistics and export to Excel

## File Format Examples

### Planilla .txt Format

```
# PLANILLA PILA
# Planilla: PL-2024-10-001
# Periodo: 2024-10
NIT: 900123456
Razon Social: EMPRESA EJEMPLO S.A.S.
Fecha Pago: 2024-10-15

# Detalles
CC|12345678|JUAN PEREZ|3500000|30
CC|87654321|MARIA GOMEZ|4000000|30

# Totales
RENGLON 31 - APORTES: 1500000 450000 600000 150000 100000 50000 50000
RENGLON 36 - MORA: 0 0 0 0
RENGLON 39 - TOTAL: 1500000 1500000 0 0 0 1500000
```

### Excel Log Format

The Excel file should contain columns with:
- Text columns: NIT, company names, descriptions
- Numeric columns: Payment amounts, values
- Any structure - the system searches all columns

## Key Features

### Comprehensive Field Display
The tipo3 parser extracts and displays **ALL available fields** for each renglon (line):
- No field truncation
- Complete data visibility
- Pandas display options configured to show all columns

### Robust File Handling
- Multiple encoding support (utf-8, latin-1, cp1252, iso-8859-1)
- Error handling and reporting
- Graceful degradation for missing data

### Detailed Matching Reports
- Match statistics
- Breakdown of no-match reasons
- Percentage differences for matched values
- Export to Excel with all results

## Configuration

### Pandas Display Settings

For optimal field visibility, the notebook sets:

```python
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)        # No width limit
pd.set_option('display.max_colwidth', None) # No column width limit
```

### Matching Tolerance

Default value tolerance is ±5% and can be adjusted in the matching function:

```python
tolerance = valor_total * 0.05  # Change 0.05 to desired percentage
```

## Output

The system generates:
1. **Console output**: Detailed processing logs with emojis for easy reading
2. **DataFrame displays**: All parsed data with complete field visibility
3. **Excel export**: `resultados_matching.xlsx` with multiple sheets:
   - Matches: All matching results
   - Renglon_31_Aportes: All R31 data with all fields
   - Renglon_36_Mora: All R36 data with all fields
   - Renglon_39_Total: All R39 data with all fields
   - Encabezados: Header information

## Testing

Sample data is provided in the `Planillas/` directory:
- `planilla_001.txt`: Sample planilla with NIT 900123456
- `planilla_002.txt`: Sample planilla with NIT 900654321
- `LOG FINANCIERO FPOB OCTUBRE .xlsx`: Sample Excel log

Run the notebook to test the complete workflow with sample data.

## Dependencies

Required Python packages:
```
pandas>=2.1.3
openpyxl>=3.1.2
```

Install with:
```bash
pip install pandas openpyxl
```

## Troubleshooting

### Issue: Parser not extracting values correctly
**Solution**: Check that the .txt file format matches the expected structure. The parser uses regex to identify renglones and extract numeric values.

### Issue: No matches found
**Solution**: 
- Verify NIT is present in the Excel log
- Check that values are within ±5% tolerance
- Ensure both NIT and value appear in the same row

### Issue: Fields not displaying
**Solution**: Make sure pandas display options are set correctly (see Configuration section).

## Future Enhancements

Potential improvements:
- Support for additional renglon types
- Configurable matching criteria
- GUI interface for non-technical users
- Batch processing with parallel execution
- Machine learning for fuzzy matching

## License

[Your License Here]

## Support

For issues or questions, please contact the repository maintainer.
