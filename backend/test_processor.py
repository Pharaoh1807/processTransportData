import io
import unittest
import pandas as pd
from processor import TransportDataProcessor

class TestTransportDataProcessor(unittest.TestCase):

    def setUp(self):
        # Create a sample SAP DataFrame resembling datavc.xlsx with header at row index 4
        raw_rows = [
            ["SAP Export Header Note", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["System: Production SAP ERP", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["Generated Date: 2026-09-19", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            # Row 4 (5th line) is the header line
            ["Plan Issue Date", "Settlement Date", "Service Agent", "Short Name", "Plant", "Shipment Number", "Is Return", "Ship To", "Province Name", "Route Code", "Delivery Type", "Material Name", "Base Unit", "Qty", "Tons Calc", "ZF01", "ZSC1", "ZT01", "Total Amt"],
            [46143, 46145, "AG001", "HTL", "PL01", "SHP001", "False", "ST01", "Hà Nội", "R001", "ZTO6", "SP01", "CHA", 100, 15.5, 1500000, 200000, 100000, 1800000],
            [46144, 46146, "AG002", "VẠN THIÊN PHÚC", "PL01", "SHP002", "False", "ST02", "Đà Nẵng", "R002", "ZLR1", "SP02", "HOP", 200, 25.0, 2500000, 300000, 150000, 2950000],
            [46145, 46147, "AG001", "HTL", "PL02", "SHP003", "False", "ST03", "TP.HCM", "R003", "ZTO6", "SP01", "CHA", 150, 18.2, 1800000, 100000, 50000, 1950000],
            [46146, 46148, "AG003", "HƯƠNG SEN", "PL01", "SHP004", "True", "ST04", "Hà Nội", "R001", "ZLF1", "SP03", "CHA", 50, 5.0, 500000, 50000, 20000, 570000]
        ]
        
        # Save to BytesIO Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            pd.DataFrame(raw_rows).to_excel(writer, sheet_name='DataVC', index=False, header=False)
        self.excel_bytes = excel_buffer.getvalue()

    def test_header_detection_and_date_parsing(self):
        processor = TransportDataProcessor.load_excel(self.excel_bytes, sheet_name='DataVC')
        df = processor.df

        self.assertIn('carrier_name', df.columns)
        self.assertIn('province', df.columns)
        self.assertIn('tons', df.columns)
        
        # Check rows count (excluding header rows & return row filtering behavior)
        self.assertEqual(len(df), 4)

        # Check date parsing from Excel serial 46143 -> Year 2026
        self.assertEqual(df.iloc[0]['year'], 2026)
        self.assertEqual(df.iloc[0]['carrier_name'], 'HTL')
        self.assertEqual(df.iloc[1]['carrier_name'], 'VẠN THIÊN PHÚC')

    def test_kpis_calculation(self):
        processor = TransportDataProcessor.load_excel(self.excel_bytes, sheet_name='DataVC')
        
        # Default exclude_return=True: should process 3 non-return rows (15.5 + 25.0 + 18.2 = 58.7 tons)
        kpis = processor.get_kpis({'exclude_return': True})
        self.assertAlmostEqual(kpis['total_tons'], 58.7)
        self.assertEqual(kpis['carrier_count'], 2) # HTL, VẠN THIÊN PHÚC
        self.assertEqual(kpis['shipment_count'], 3)
        self.assertEqual(kpis['province_count'], 3) # Hà Nội, Đà Nẵng, TP.HCM
        self.assertGreater(kpis['avg_unit_price'], 0)
        self.assertEqual(kpis['return_rate'], 25.0) # 1 return out of 4 total = 25%

    def test_matrix_and_charts(self):
        processor = TransportDataProcessor.load_excel(self.excel_bytes, sheet_name='DataVC')
        charts = processor.get_charts_data({'exclude_return': True})

        self.assertIn('carrierRanking', charts)
        self.assertIn('carrierProvinceMatrix', charts)
        self.assertIn('costBreakdown', charts)

        matrix = charts['carrierProvinceMatrix']
        self.assertIn('HTL', matrix['carriers'])
        self.assertIn('HÀ NỘI', matrix['provinces'])

    def test_excel_export(self):
        processor = TransportDataProcessor.load_excel(self.excel_bytes, sheet_name='DataVC')
        excel_bytes = processor.export_excel({'exclude_return': True})
        self.assertGreater(len(excel_bytes), 1000)

if __name__ == '__main__':
    unittest.main()
