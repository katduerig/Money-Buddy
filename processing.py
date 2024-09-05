import sheets #imports data

from datetime import datetime

total_data=sheets.get_all_data()


number_to_month= {
    "1":"January",
    "2":"February",
    "3": "March",
    "4": "April",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "August",
    "9": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}
def clean_cost(cost): # removes the dollar sign and any extra spaces, turns cost into float
    cost_no_sign= cost.replace("$","").strip()
    cost_no_sign= cost_no_sign.replace(",","").strip()
    cost_float=float(cost_no_sign)
    return cost_float


def get_all_totals(total_data):
    totals={}

    for row in total_data[1:]:
        if len(row) > 0:  # if row is not blank, looks at row
            date = row[0]
            cost = row[1]

            # converts cost to float
            cost_float = clean_cost(cost)

            # turns date into array of 3, month/day/year
            date_array = date.split("/")  
            row_month = date_array[0]
            row_year = date_array[2]

            month=number_to_month[row_month]
            key= str(month) + " " + "20" + str(row_year)
            if key not in totals:
                totals[key]=cost_float
            else:
                totals[key]+=cost_float
                totals[key]=round(totals[key],2)
    formatted_totals = {key: f"${value:,.2f}" for key, value in totals.items()}
    return formatted_totals


def get_monthly_category_totals():
    data = total_data[1:]
    sums = {}

    for row in data:
        if row== []:
            continue
       
        date, amount, category = row[0], row[1], row[2]
        category = category.strip()

        date = datetime.strptime(date, '%m/%d/%y')  # convert 'Date' to datetime
        amount = float(clean_cost(amount))  # convert 'Amount' to float

        # extract the year and month as a tuple
        friendly_month = number_to_month[str(date.month)]
        timeKey= f"{friendly_month} {date.year}"

        if timeKey in sums:
            if category in sums[timeKey]:
                sums[timeKey][category]+=amount
            else:
                sums[timeKey][category]=amount
        else:
            sums[timeKey]={}
            if category in sums[timeKey]:
                sums[timeKey][category]+=amount
            else:
                sums[timeKey][category]=amount


    return sums