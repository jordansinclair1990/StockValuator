import re
from numpy import polyfit
from stockexchangemapping import exchange_mapping_dict
import requests


def getTickerPrice(ticker):
    url = 'https://www.marketwatch.com/investing/stock/{}'.format(ticker)
    source = requests.get(url).text
    price = float(source.split('class="last-value">')[1].split('</span>')[0])
    return price

def getPageSourceCode(ticker):
    find_exchange = exchange_mapping_dict
    urlstart = 'https://financials.morningstar.com/finan/financials/getFinancePart.html'
    urlend = '?t={}:{}&region=usa&culture=en-US&cur=&order=asc'.format(find_exchange[ticker], ticker)
    url = '{}{}'.format(urlstart, urlend)
    page = requests.get(url)
    page_source_code = page.json()['componentData']
        
    return page_source_code

def getSpittingDataFromPage(source_code):
    regex_pattern = r'"Y\d{1,2} i90">.{1,8}</td>'
    splitting_data = re.findall(regex_pattern, source_code)
    del splitting_data[-1]

    return splitting_data

def split_data_into_FCF_data(splitting_data):
    #returns 2 lists: a number representing the number of years ago the corresponding data
    #point was. and the EPS for that year.
    year_number_list = []
    eps_list = []
    enum_splitting_data = list(enumerate(splitting_data))
    for year_number, eps in enum_splitting_data:
        try:
            inner_data = float(eps.split('">')[1].split('<')[0])
            year_number_list.append(year_number - 9)
            eps_list.append(inner_data)
        except Exception as e:
            pass
    return year_number_list, eps_list

def splitOutFCFData(splitting_data):
    year_number_list = []
    eps_list = []
    enum_splitting_data = list(enumerate(splitting_data))
    for year_number, eps in enum_splitting_data:
        try:
            inner_data = float(eps.split('">')[1].split('<')[0])
            year_number_list.append(year_number - 9)
            eps_list.append(inner_data)
        except Exception as e:
            pass
    regression_coefficients = list(polyfit(year_number_list, eps_list, 1))
    slope = regression_coefficients[0]
    y_intercept = regression_coefficients[1]
    return year_number_list, eps_list, slope, y_intercept

def getFCFData(ticker):
    source_code = getPageSourceCode(ticker)
    splitting_data = getSpittingDataFromPage(source_code)
    FCF_data = splitOutFCFData(splitting_data)
    return FCF_data

def applyDiscount(FCF_datapoint, year_number, discount_rate_percent=11):
    discount_rate = (discount_rate_percent + 100) / 100
    discounted_value = FCF_datapoint / (discount_rate**year_number)
    return discounted_value

def projectFutureYearFCF(FCF_data, year_number):
    slope = FCF_data[2]
    y_intercept = FCF_data[3]
    projected_FCF = slope*year_number + y_intercept
    return projected_FCF    

def projectDiscountedFutureYearFCF(FCF_data, year_number, discount_rate_percent=11):
    projected_FCF = projectFutureYearFCF(FCF_data, year_number)
    discounted_projected_FCF = applyDiscount(projected_FCF, year_number)
    return discounted_projected_FCF

def getTerminalValue(FCF_data, 
                     start_after_year,
                     growth_rate_percent=2,
                     discount_rate_percent=11):

    initial_cash_flow = projectDiscountedFutureYearFCF(FCF_data,
                                                           (start_after_year),
                                                            discount_rate_percent)
    growth_rate = growth_rate_percent / 100
    discount_rate = discount_rate_percent / 100
    terminal_value = (initial_cash_flow * (1 + growth_rate)) / (discount_rate - growth_rate)
    return terminal_value
    
def performDcfOnStockData(FCF_data, 
                          forecast_period=5,
                          growth_rate_percent=2,
                          discount_rate_percent=11):
    discounted_cash_flows = []
    for i in range(1,(forecast_period+1)):
        cash_flow = projectDiscountedFutureYearFCF(FCF_data,
                                                        i,
                                                        discount_rate_percent)
        discounted_cash_flows.append(cash_flow)
    terminal_value = getTerminalValue(FCF_data,
                                      forecast_period,
                                      growth_rate_percent,
                                      discount_rate_percent)
    discounted_cash_flows.append(terminal_value)
    dcf_value = round(sum(discounted_cash_flows),2)
    return dcf_value


def grabStockDataAndCalculateDCF(ticker,
                                 forecast_period=5, 
                                 growth_rate_percent=2, 
                                 discount_rate_percent=11):   
    FCF_data = getFCFData(ticker)
    dcf_value = performDcfOnStockData(FCF_data,
                                      forecast_period, 
                                      growth_rate_percent, 
                                      discount_rate_percent)
    return_string = 'Ticker: {}, DCF-Value: {}'.format(ticker, dcf_value)
    return return_string

def userInput():

    print('Enter a Ticker: ')
    input_prompt = input().upper()
    ticker = str(input_prompt)
    
    end_loop = 0
    while end_loop == 0:
        default_settings_prompt = input('Would you like to run with the default settings? (Y/n)').upper()
        if (default_settings_prompt == '') or (default_settings_prompt == 'Y'):
            end_loop = 1
            print(grabStockDataAndCalculateDCF(ticker))
        elif default_settings_prompt == 'N':
            forecast_period = int(input('Enter number of years for short-term forecast: '))
            growth_rate = float(input('Enter % growth rate: '))
            discount_rate = float(input('Enter % discount rate :'))
            end_loop = 1
            print(grabStockDataAndCalculateDCF(ticker,
                                         forecast_period,
                                         growth_rate,
                                         discount_rate))
        else:
            pass
        print('Current price: {}'.format(getTickerPrice(ticker)))
            
    return None
    

userInput()
