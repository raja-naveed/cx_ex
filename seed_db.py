import os
import sys
from datetime import time, date
from decimal import Decimal

sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import (User, Stock, PriceLive, MarketHours, MarketCalendar, 
                       MarketState, CashLedger, CashTransactionType, UserRole)

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Create admin user
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(email=admin_email, role=UserRole.ADMIN)
            admin.set_password(admin_password)
            db.session.add(admin)
            print(f"Created admin user: {admin_email}")
        
        # Create sample customer
        customer = User.query.filter_by(email='demo@example.com').first()
        if not customer:
            customer = User(email='demo@example.com', role=UserRole.CUSTOMER)
            customer.set_password('demo123')
            db.session.add(customer)
            db.session.commit()  # Commit to get the ID
            
            # Give demo user some starting cash
            initial_cash = CashLedger(
                user_id=customer.id,
                transaction_type=CashTransactionType.DEPOSIT,
                amount=Decimal('10000.00'),
                description='Initial demo balance'
            )
            db.session.add(initial_cash)
            print("Created demo user with $10,000 starting balance")
        
        # Create market hours (Monday-Friday, 9:30 AM - 4:00 PM Eastern)
        for day in range(5):  # Monday = 0, Friday = 4
            market_hour = MarketHours.query.filter_by(day_of_week=day).first()
            if not market_hour:
                market_hour = MarketHours(
                    day_of_week=day,
                    open_time=time(9, 30),
                    close_time=time(16, 0),
                    is_active=True
                )
                db.session.add(market_hour)
        
        # Initialize market state
        market_state = MarketState.query.first()
        if not market_state:
            market_state = MarketState(is_open=False)
            db.session.add(market_state)
        
        # Create sample stocks
        sample_stocks = [
               {'ticker': 'XXBZR', 'company': 'Helix Software PLC', 'float_shares': 13109095636, 'initial_price': Decimal('217.23')},
    {'ticker': 'RMG', 'company': 'Harbor Entertainment PLC', 'float_shares': 16440348471, 'initial_price': Decimal('88.88')},
    {'ticker': 'QCMU', 'company': 'Pioneer Digital Holdings', 'float_shares': 11384756150, 'initial_price': Decimal('53.33')},
    {'ticker': 'KGEI', 'company': 'Greenfield Logistics Corp.', 'float_shares': 2652679899, 'initial_price': Decimal('141.17')},
    {'ticker': 'WQQN', 'company': 'Cobalt Financial PLC', 'float_shares': 3936013136, 'initial_price': Decimal('325.28')},
    {'ticker': 'VQK', 'company': 'Redwood Foods Group', 'float_shares': 17021307990, 'initial_price': Decimal('278.67')},
    {'ticker': 'MUT', 'company': 'Prospera Apparel Inc.', 'float_shares': 12671055841, 'initial_price': Decimal('356.64')},
    {'ticker': 'VXV', 'company': 'Atlas Materials Ltd.', 'float_shares': 9116000632, 'initial_price': Decimal('140.05')},
    {'ticker': 'YWE', 'company': 'Apex Mining Corp.', 'float_shares': 17947862162, 'initial_price': Decimal('102.60')},
    {'ticker': 'KUP', 'company': 'Cypress Analytics Group', 'float_shares': 12889118777, 'initial_price': Decimal('78.31')},
    {'ticker': 'KZL', 'company': 'Ironclad Networks Holdings', 'float_shares': 15777264214, 'initial_price': Decimal('128.56')},
    {'ticker': 'JYWQ', 'company': 'Citadel Water Inc.', 'float_shares': 16040849713, 'initial_price': Decimal('293.25')},
    {'ticker': 'ZDS', 'company': 'TrueNorth Telecom PLC', 'float_shares': 10502693662, 'initial_price': Decimal('188.46')},
    {'ticker': 'DCH', 'company': 'Granite Security PLC', 'float_shares': 12749005936, 'initial_price': Decimal('221.64')},
    {'ticker': 'GQH', 'company': 'OpenGate Marine Group', 'float_shares': 13398973433, 'initial_price': Decimal('58.42')},
    {'ticker': 'LBN', 'company': 'Nimbus Media Ltd.', 'float_shares': 18144516026, 'initial_price': Decimal('94.56')},
    {'ticker': 'MWQ', 'company': 'Beacon Realty PLC', 'float_shares': 9442312278, 'initial_price': Decimal('346.51')},
    {'ticker': 'ZMR', 'company': 'Cascade Mobility Corp.', 'float_shares': 15805548077, 'initial_price': Decimal('158.66')},
    {'ticker': 'HQS', 'company': 'Vertex Electric Holdings', 'float_shares': 18853493636, 'initial_price': Decimal('207.63')},
    {'ticker': 'JXW', 'company': 'Aurora Pharmaceuticals PLC', 'float_shares': 11595655591, 'initial_price': Decimal('214.65')},
    {'ticker': 'ZGL', 'company': 'Solace Automotive Group', 'float_shares': 18062441544, 'initial_price': Decimal('160.02')},
    {'ticker': 'GXC', 'company': 'Monarch Analytics Holdings', 'float_shares': 18460624832, 'initial_price': Decimal('164.47')},
    {'ticker': 'XDG', 'company': 'Northwind Marine Ltd.', 'float_shares': 13360207328, 'initial_price': Decimal('74.59')},
    {'ticker': 'NLI', 'company': 'Sapphire Logistics Inc.', 'float_shares': 18363545390, 'initial_price': Decimal('164.36')},
    {'ticker': 'IFX', 'company': 'Sunstone Networks PLC', 'float_shares': 17853752661, 'initial_price': Decimal('230.27')},
    {'ticker': 'VYO', 'company': 'FirstPoint Cloud Group', 'float_shares': 12965773012, 'initial_price': Decimal('364.34')},
    {'ticker': 'DBE', 'company': 'Polar Digital Inc.', 'float_shares': 12282042653, 'initial_price': Decimal('72.75')},
    {'ticker': 'EIK', 'company': 'Seabright Energy PLC', 'float_shares': 12178141176, 'initial_price': Decimal('315.90')},
    {'ticker': 'UCP', 'company': 'Mesa Biotech Corp.', 'float_shares': 11422646277, 'initial_price': Decimal('120.26')},
    {'ticker': 'OAF', 'company': 'Apex Materials PLC', 'float_shares': 15538215823, 'initial_price': Decimal('206.66')},
    {'ticker': 'TQS', 'company': 'Equinox Entertainment Inc.', 'float_shares': 11706082922, 'initial_price': Decimal('292.49')},
    {'ticker': 'HSR', 'company': 'Crown Networks Holdings', 'float_shares': 19700821144, 'initial_price': Decimal('128.62')},
    {'ticker': 'PZC', 'company': 'Arcadia Software Ltd.', 'float_shares': 17724680756, 'initial_price': Decimal('381.38')},
    {'ticker': 'JYG', 'company': 'Stellar Electric Group', 'float_shares': 18453227654, 'initial_price': Decimal('194.13')},
    {'ticker': 'FGA', 'company': 'Prospera Apparel PLC', 'float_shares': 17553245820, 'initial_price': Decimal('96.51')},
    {'ticker': 'QJJ', 'company': 'Driftwood Foods Group', 'float_shares': 12550277785, 'initial_price': Decimal('182.53')},
    {'ticker': 'LUS', 'company': 'Horizon Security PLC', 'float_shares': 10026397840, 'initial_price': Decimal('137.65')},
    {'ticker': 'UOF', 'company': 'TrueNorth Water Ltd.', 'float_shares': 19084326278, 'initial_price': Decimal('239.83')},
    {'ticker': 'JZO', 'company': 'Brightwave Analytics Corp.', 'float_shares': 12192334308, 'initial_price': Decimal('256.00')},
    {'ticker': 'KXH', 'company': 'Atlas Mobility PLC', 'float_shares': 15258507738, 'initial_price': Decimal('251.19')},
    {'ticker': 'YQO', 'company': 'Greenfield Mining Inc.', 'float_shares': 17486110356, 'initial_price': Decimal('105.92')},
    {'ticker': 'ZAS', 'company': 'Northwind Media PLC', 'float_shares': 19522398911, 'initial_price': Decimal('230.63')},
    {'ticker': 'HYP', 'company': 'Helix Telecom Group', 'float_shares': 17158049710, 'initial_price': Decimal('167.36')},
    {'ticker': 'XSI', 'company': 'Beacon Mining Holdings', 'float_shares': 17517035831, 'initial_price': Decimal('318.14')},
    {'ticker': 'QJD', 'company': 'Orion Financial Inc.', 'float_shares': 16569528964, 'initial_price': Decimal('227.90')},
    {'ticker': 'YXP', 'company': 'OpenGate Foods PLC', 'float_shares': 10498874562, 'initial_price': Decimal('172.92')},
    {'ticker': 'RLL', 'company': 'Cypress Logistics Group', 'float_shares': 14998290297, 'initial_price': Decimal('214.40')},
    {'ticker': 'IZH', 'company': 'Pioneer Realty Inc.', 'float_shares': 16147598458, 'initial_price': Decimal('304.38')},
    {'ticker': 'VNH', 'company': 'Equinox Software PLC', 'float_shares': 14645261647, 'initial_price': Decimal('100.13')},
    {'ticker': 'MCA', 'company': 'Arcadia Networks Ltd.', 'float_shares': 12698135458, 'initial_price': Decimal('210.18')},
    {'ticker': 'BIR', 'company': 'Crown Materials Inc.', 'float_shares': 16517417128, 'initial_price': Decimal('215.25')},
    {'ticker': 'GEW', 'company': 'Horizon Automotive Holdings', 'float_shares': 17148763156, 'initial_price': Decimal('203.65')},
    {'ticker': 'CUE', 'company': 'Riverton Systems PLC', 'float_shares': 16883558740, 'initial_price': Decimal('267.14')},
    {'ticker': 'LNM', 'company': 'Granite Marine Group', 'float_shares': 19120981090, 'initial_price': Decimal('158.33')},
    {'ticker': 'KMB', 'company': 'Apex Robotics Corp.', 'float_shares': 15225608733, 'initial_price': Decimal('190.60')},
    {'ticker': 'GCO', 'company': 'Silverline Telecom Ltd.', 'float_shares': 10892292569, 'initial_price': Decimal('197.64')},
    {'ticker': 'ESD', 'company': 'Northwind Security PLC', 'float_shares': 18978016924, 'initial_price': Decimal('241.86')},
    {'ticker': 'ZMF', 'company': 'Harbor Cloud Group', 'float_shares': 11867432030, 'initial_price': Decimal('262.73')},
    {'ticker': 'YCI', 'company': 'Cypress Media Holdings', 'float_shares': 10217801133, 'initial_price': Decimal('257.85')},
    {'ticker': 'LQK', 'company': 'Falcon Analytics PLC', 'float_shares': 11021662077, 'initial_price': Decimal('225.41')},
    {'ticker': 'WQO', 'company': 'BlueLake Financial Group', 'float_shares': 14793243693, 'initial_price': Decimal('120.42')},
    {'ticker': 'WZL', 'company': 'Mesa Retail Inc.', 'float_shares': 17795825385, 'initial_price': Decimal('269.73')},
    {'ticker': 'GZC', 'company': 'Helix Telecom Holdings', 'float_shares': 18651440505, 'initial_price': Decimal('116.78')},
    {'ticker': 'ZBP', 'company': 'Apex Realty Group', 'float_shares': 16274138754, 'initial_price': Decimal('316.36')},
    {'ticker': 'KTF', 'company': 'OpenGate Hardware PLC', 'float_shares': 13247696622, 'initial_price': Decimal('63.53')},
    {'ticker': 'JRT', 'company': 'Prospera Electric Ltd.', 'float_shares': 14696093271, 'initial_price': Decimal('146.20')},
    {'ticker': 'QTR', 'company': 'Titan Mining PLC', 'float_shares': 16757352002, 'initial_price': Decimal('168.86')},
    {'ticker': 'YLV', 'company': 'Aurora Pharmaceuticals Group', 'float_shares': 16491962075, 'initial_price': Decimal('119.51')},
    {'ticker': 'KGA', 'company': 'Nimbus Water Corp.', 'float_shares': 18021421777, 'initial_price': Decimal('176.62')},
    {'ticker': 'DYM', 'company': 'Sapphire Foods PLC', 'float_shares': 19188753649, 'initial_price': Decimal('95.88')},
    {'ticker': 'NQJ', 'company': 'Citadel Materials Inc.', 'float_shares': 18195502232, 'initial_price': Decimal('174.17')},
    {'ticker': 'NAT', 'company': 'Redwood Holdings PLC', 'float_shares': 18534792006, 'initial_price': Decimal('87.47')},
    {'ticker': 'MBD', 'company': 'Vantage Apparel Group', 'float_shares': 18857890372, 'initial_price': Decimal('230.19')},
    {'ticker': 'VFE', 'company': 'Horizon Digital Ltd.', 'float_shares': 13725572303, 'initial_price': Decimal('211.31')},
    {'ticker': 'FJY', 'company': 'Northwind Mobility PLC', 'float_shares': 14395986161, 'initial_price': Decimal('344.49')},
    {'ticker': 'QPV', 'company': 'Ironclad Mining Holdings', 'float_shares': 14173746440, 'initial_price': Decimal('105.31')},
    {'ticker': 'QEY', 'company': 'Beacon Electric Group', 'float_shares': 11401279033, 'initial_price': Decimal('96.60')},
    {'ticker': 'PHJ', 'company': 'OpenGate Entertainment PLC', 'float_shares': 18050341153, 'initial_price': Decimal('220.94')},
    {'ticker': 'XEL', 'company': 'BlueLake Security Group', 'float_shares': 11801683818, 'initial_price': Decimal('248.16')},
    {'ticker': 'VZF', 'company': 'Skyward Software Holdings', 'float_shares': 17403306598, 'initial_price': Decimal('221.43')},
    {'ticker': 'GAD', 'company': 'Titan Systems Ltd.', 'float_shares': 12288005038, 'initial_price': Decimal('293.15')},
    {'ticker': 'DQT', 'company': 'Equinox Networks Corp.', 'float_shares': 14261100850, 'initial_price': Decimal('238.75')},
    {'ticker': 'ZRS', 'company': 'Falcon Media PLC', 'float_shares': 16585552555, 'initial_price': Decimal('187.39')},
    {'ticker': 'KUD', 'company': 'Crown Logistics Group', 'float_shares': 10732360353, 'initial_price': Decimal('209.70')},
    {'ticker': 'KXN', 'company': 'Apex Financial Inc.', 'float_shares': 13669675448, 'initial_price': Decimal('345.65')},
    {'ticker': 'XBA', 'company': 'Prospera Digital PLC', 'float_shares': 13094796740, 'initial_price': Decimal('210.32')},
    {'ticker': 'LJS', 'company': 'Polar Technologies Holdings', 'float_shares': 18022153595, 'initial_price': Decimal('291.24')},
    {'ticker': 'RDR', 'company': 'Summit Robotics Group', 'float_shares': 19790975053, 'initial_price': Decimal('135.15')},
    {'ticker': 'YAP', 'company': 'Sapphire Networks Corp.', 'float_shares': 18480974470, 'initial_price': Decimal('181.54')},
    {'ticker': 'WGG', 'company': 'Cascade Apparel PLC', 'float_shares': 18231511291, 'initial_price': Decimal('208.85')},
    {'ticker': 'RJP', 'company': 'Ember Mining PLC', 'float_shares': 17864688059, 'initial_price': Decimal('201.73')},
    {'ticker': 'QAH', 'company': 'Citadel Logistics Inc.', 'float_shares': 15042830118, 'initial_price': Decimal('238.09')},
    {'ticker': 'HML', 'company': 'Driftwood Media Ltd.', 'float_shares': 14610835546, 'initial_price': Decimal('140.24')},
    {'ticker': 'KUZ', 'company': 'Aurora Energy Group', 'float_shares': 11944387947, 'initial_price': Decimal('203.05')},
    {'ticker': 'YQC', 'company': 'BroadPeak Financial PLC', 'float_shares': 10398163160, 'initial_price': Decimal('176.44')},
    {'ticker': 'QVF', 'company': 'Ventura Water PLC', 'float_shares': 17063700151, 'initial_price': Decimal('221.85')},
    {'ticker': 'CEK', 'company': 'Mesa Digital Holdings', 'float_shares': 10644419822, 'initial_price': Decimal('256.59')},
    {'ticker': 'LQO', 'company': 'Ironclad Apparel Group', 'float_shares': 10761805005, 'initial_price': Decimal('188.67')},
    {'ticker': 'QKB', 'company': 'Redwood Marine PLC', 'float_shares': 17326425048, 'initial_price': Decimal('158.53')},
    {'ticker': 'QXV', 'company': 'OpenGate Materials Ltd.', 'float_shares': 16510309849, 'initial_price': Decimal('199.11')},
    {'ticker': 'IKX', 'company': 'Vantage Foods Inc.', 'float_shares': 17496191855, 'initial_price': Decimal('101.96')},
    {'ticker': 'YGI', 'company': 'Beacon Entertainment PLC', 'float_shares': 16182263388, 'initial_price': Decimal('130.69')},
    {'ticker': 'QHX', 'company': 'Arcadia Cloud Group', 'float_shares': 19195024127, 'initial_price': Decimal('192.38')},
    {'ticker': 'NTZ', 'company': 'Ember Electric Holdings', 'float_shares': 18382330713, 'initial_price': Decimal('138.92')},
    {'ticker': 'ZIG', 'company': 'Cobalt Hardware Corp.', 'float_shares': 12001995346, 'initial_price': Decimal('285.77')},
    {'ticker': 'WVM', 'company': 'Atlas Software PLC', 'float_shares': 14685167909, 'initial_price': Decimal('176.76')},
    {'ticker': 'GZJ', 'company': 'Northwind Analytics PLC', 'float_shares': 11874153807, 'initial_price': Decimal('224.33')},
    {'ticker': 'OIJ', 'company': 'Keystone Realty Group', 'float_shares': 18640444787, 'initial_price': Decimal('173.25')},
    {'ticker': 'YUD', 'company': 'Solace Mining PLC', 'float_shares': 11735487563, 'initial_price': Decimal('232.72')},
    {'ticker': 'KWD', 'company': 'Citadel Media Corp.', 'float_shares': 13354660517, 'initial_price': Decimal('356.22')},
    {'ticker': 'ZQT', 'company': 'Seabright Materials PLC', 'float_shares': 14395443113, 'initial_price': Decimal('225.45')},
    {'ticker': 'RVS', 'company': 'Apex Networks Inc.', 'float_shares': 18298704211, 'initial_price': Decimal('228.56')},
    {'ticker': 'QEZ', 'company': 'Granite Apparel PLC', 'float_shares': 16801547641, 'initial_price': Decimal('249.08')},
    {'ticker': 'WJG', 'company': 'Monarch Software Ltd.', 'float_shares': 16906754293, 'initial_price': Decimal('269.61')},
    {'ticker': 'VTC', 'company': 'Equinox Financial PLC', 'float_shares': 13131576200, 'initial_price': Decimal('300.42')},
    {'ticker': 'NHE', 'company': 'OpenGate Robotics Group', 'float_shares': 11295784580, 'initial_price': Decimal('260.26')},
    {'ticker': 'KMS', 'company': 'Harbor Water PLC', 'float_shares': 16976747039, 'initial_price': Decimal('177.43')},
    {'ticker': 'JYO', 'company': 'Crown Aerospace Inc.', 'float_shares': 10856016250, 'initial_price': Decimal('232.41')},
    {'ticker': 'FZG', 'company': 'Arcadia Media PLC', 'float_shares': 10690872812, 'initial_price': Decimal('160.05')},
    {'ticker': 'YBQ', 'company': 'Ventura Security Holdings', 'float_shares': 18934308364, 'initial_price': Decimal('316.57')},
    {'ticker': 'TUV', 'company': 'Solace Realty PLC', 'float_shares': 14563535275, 'initial_price': Decimal('118.53')},
    {'ticker': 'LMP', 'company': 'Horizon Systems Ltd.', 'float_shares': 17999902228, 'initial_price': Decimal('185.26')},
    {'ticker': 'WQK', 'company': 'Polar Entertainment PLC', 'float_shares': 17239247438, 'initial_price': Decimal('171.49')},
    {'ticker': 'HYA', 'company': 'Beacon Marine Corp.', 'float_shares': 17901097256, 'initial_price': Decimal('260.67')},
    {'ticker': 'XPF', 'company': 'Titan Retail PLC', 'float_shares': 15250100271, 'initial_price': Decimal('227.66')},
    {'ticker': 'QOF', 'company': 'Aurora Analytics Group', 'float_shares': 14061133991, 'initial_price': Decimal('165.11')},
    {'ticker': 'KQW', 'company': 'Apex Pharmaceuticals Ltd.', 'float_shares': 11508592906, 'initial_price': Decimal('151.94')},
    {'ticker': 'ZPG', 'company': 'Nimbus Robotics PLC', 'float_shares': 14713847421, 'initial_price': Decimal('248.20')},
    {'ticker': 'YHN', 'company': 'Clearline Media Holdings', 'float_shares': 17751436577, 'initial_price': Decimal('147.50')},
    {'ticker': 'VCE', 'company': 'Summit Digital Corp.', 'float_shares': 16864738737, 'initial_price': Decimal('180.14')},
    {'ticker': 'QLZ', 'company': 'Seabright Marine Group', 'float_shares': 15164053080, 'initial_price': Decimal('221.72')},
    {'ticker': 'XQC', 'company': 'OpenGate Financial PLC', 'float_shares': 10230607389, 'initial_price': Decimal('282.24')},
    {'ticker': 'TAM', 'company': 'Sapphire Biotech PLC', 'float_shares': 17626216250, 'initial_price': Decimal('138.51')},
    {'ticker': 'RKH', 'company': 'Redwood Networks Ltd.', 'float_shares': 11379692316, 'initial_price': Decimal('215.63')},
    {'ticker': 'QGL', 'company': 'Arcadia Technologies Group', 'float_shares': 17395077836, 'initial_price': Decimal('237.27')},
    {'ticker': 'UQL', 'company': 'GoldenBridge Logistics PLC', 'float_shares': 17428660723, 'initial_price': Decimal('273.35')},
    {'ticker': 'YJR', 'company': 'BlueLake Foods Holdings', 'float_shares': 17302107027, 'initial_price': Decimal('167.64')},
    {'ticker': 'PWH', 'company': 'Riverton Automotive Corp.', 'float_shares': 10177902637, 'initial_price': Decimal('205.19')},
    {'ticker': 'QIN', 'company': 'Apex Electric PLC', 'float_shares': 13654085966, 'initial_price': Decimal('220.40')},
    {'ticker': 'XQI', 'company': 'Ironclad Hardware Group', 'float_shares': 12663481768, 'initial_price': Decimal('171.28')},
    {'ticker': 'YLM', 'company': 'Vertex Cloud PLC', 'float_shares': 19935607768, 'initial_price': Decimal('273.41')},
    {'ticker': 'RKG', 'company': 'Mesa Security PLC', 'float_shares': 16214200466, 'initial_price': Decimal('172.83')},
    {'ticker': 'KAL', 'company': 'Citadel Financial Ltd.', 'float_shares': 18305297856, 'initial_price': Decimal('244.86')},
    {'ticker': 'ZUP', 'company': 'OpenGate Mobility PLC', 'float_shares': 12445988338, 'initial_price': Decimal('212.54')},
    {'ticker': 'WYU', 'company': 'Cypress Mining Group', 'float_shares': 14692411505, 'initial_price': Decimal('179.28')},
    {'ticker': 'HFZ', 'company': 'Beacon Foods PLC', 'float_shares': 14931153327, 'initial_price': Decimal('232.11')},
    {'ticker': 'JPT', 'company': 'Aurora Marine PLC', 'float_shares': 18988606168, 'initial_price': Decimal('247.93')}
        ]
        
        for stock_data in sample_stocks:
            stock = Stock.query.filter_by(ticker=stock_data['ticker']).first()
            if not stock:
                stock = Stock(**stock_data, is_active=True)
                db.session.add(stock)
                db.session.commit()
                
                # Initialize price data
                price_live = PriceLive.initialize_from_stock(stock)
                db.session.commit()
                print(f"Created stock: {stock.ticker}")
        
        # Add some sample holidays
        sample_holidays = [
            {'date': date(2024, 1, 1), 'name': "New Year's Day"},
            {'date': date(2024, 7, 4), 'name': 'Independence Day'},
            {'date': date(2024, 12, 25), 'name': 'Christmas Day'}
        ]
        
        for holiday_data in sample_holidays:
            holiday = MarketCalendar.query.filter_by(date=holiday_data['date']).first()
            if not holiday:
                holiday = MarketCalendar(**holiday_data, is_holiday=True)
                db.session.add(holiday)
        
        db.session.commit()
        print("Database seeded successfully!")
        print(f"Admin login: {admin_email} / {admin_password}")
        print("Demo login: demo@example.com / demo123")

if __name__ == '__main__':
    seed_database()