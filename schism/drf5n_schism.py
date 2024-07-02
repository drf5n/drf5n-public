"""
Miscellanuous functions for use with SCHISM

See https://github.com/drf5n/drf5n-public/schism/drf5n_schism.py

drf5n
"""

def schismBaseDate2Datetime64(string="2014 6 7 8.00 9.00"):
    """Convert a Schism time:basedate attribute string into a numpy dateime64 type

    For example:
        schismBaseDate2Datetime64("2012 3 4 5.00 6.00")
    returns:
        Timestamp('2012-03-04 05:06:00+0000', tz='UTC')
    or:
        2012-03-04 05:06:00+00:00

    drf 2024-07-01 
    """
    import pandas
    [year,month,day, hour, minute] = string.split()
    return(pandas.to_datetime(f"{year}-{month}-{day} {hour}:{minute}Z"))

if __name__ == "__main__":
  print("""Miscellaneous functions for SCHISM
	See https://github.com/drf5n/drf5n-public/schism/drf5n_schism.py fos source

	schismBaseDate2Datetime64("2012 3 4 5.00 6.00") # convert SCHISM time:basedate attribute  to a datetiem64
	""")
