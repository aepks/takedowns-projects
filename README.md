# takedowns-projects
Sending Calendar Invites Automatically for Takedowns

# Program Hierarchy:

```
> g_api
  > authenticate.py
      calendar_auth():
        # Takes no arguments
        # Returns a 'service' object.
      sheets_auth():
        # Takes no arguments
        # Returns a 'service' object.

  > cal_session.py
    Session:
    __init__(self): # NOT IMPLEMENTED
    # Takes no arguments.
    # Instantiate things as needed for the calendar API.

    create_event(datetime, meal, individuals): # NOT IMPLEMENTED
    # Takes arguments:
      # datetime: The date as a 'datetime' object.
      # meal: Either 'lunch' or 'dinner'.
      # individuals: Dictionary of form {name: email}.

    # Checks to see if a takedowns event already exists at the specified time - if so, return False.
    # Creates a Google Calendar event at the specified time, with appropriate information.
    # After successful creation, return True.

  > sheets_session.py
    Session:
      __init__(self):
      # Takes no arguments.
      # self.service - Service object called from authenticate.sheets_auth()
      # self.takedowns_key - Taken from config, takedowns spreadsheet key.

      # self.roster_key - Taken from config, roster spreadsheet key. # NOT IMPLEMENTED

      read_takedowns_list(self):
      # Takes no arguments.
      # Calls the sheets API, and pulls the list of individuals.
      # Return a list of tuples containing the names of each individual.

      read_roster(self): # NOT IMPLEMENTED
      # Takes no arguments.
      # Return a list of tuples for each individual's name and their email.


  > spreadsheet_config.py
    Object 'config' of structure:
    'takedowns_key': [The key for the takedowns list.]
    'roster_key': [The key of the roster.] # NOT IMPLEMENTED  

> main.py # NOT IMPLEMENTED  
  Session:
    __init__(self): Initializes values:
      sheet_session
      cal_session
      takedowns_list
      roster

    process_meal(self, list):
      # Takes a list of individuals. Using self.roster, cross reference this list to their hawk emails.
      # Consider using fuzzy string matching, such as the python package 'fuzzywuzzy'.
      # Builds object of form {name: email}.
      # Using self.cal_session, create a calendar event for this.
      # Returns True if all names could be solved, returns False otherwise.



```
