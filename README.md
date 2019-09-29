# takedowns-projects
Sending Calendar Invites Automatically for Takedowns

# Program Hierarchy:

```
>g_api
  > __init__.py
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

    # Some methods to work with the API.

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
    JSON object named 'config' of structure:
    'takedowns_key': [The key for the takedowns list.]
    'roster_key': [The key of the roster.] # NOT IMPLEMENTED  

```
