import re

text = "covid-19-who-monthly-update-october-2022.pdf?sfvrsn=57f64f6b_1&download=true"


date_pattern = r"(\w+-\d{4})"


match = re.search(date_pattern, text)

if match:
   
    date = match.group(1)
    print(date)
else:
    print('에러! 패턴을 확인해주세요')
