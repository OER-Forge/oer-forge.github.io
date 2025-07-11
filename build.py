from oerforge.scan import *

def main():
    # Initialize the database and tables
    initialize_database()
    
    # Populate the site info from _config.yml into the database
    site_info = populate_site_info()
    print("Site info inserted:", site_info)
    
    # Print all rows in the 'site' table
    print("Site table contents:")
    print_table('site')
    
    # Populate the site info from _config.yml into the database
    site_info = populate_site_info()
    print("Site info inserted:", site_info)
    
    # Populate the TOC from _config.yml into the database
    populate_toc()
    print("TOC table contents:")
    print_table('toc')

if __name__ == "__main__":
    main()
