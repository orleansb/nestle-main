import requests
from bs4 import BeautifulSoup

def check_instagram_account(brand_name):
    search_url = f"https://www.instagram.com/{brand_name}/"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try to find the 'og:type' meta tag
        meta_tag = soup.find('meta', {'property': 'og:type'})
        
        # Check if the meta tag is found and its content is 'profile'
        if meta_tag and meta_tag.get('content') == 'profile':
            return True  # Instagram account found
        else:
            return False  # No Instagram account found
    else:
        return False  # Could not access Instagram

# List to store brands with Instagram accounts
brands_instagram_names = ['abuelita', 'acqua_panna', 'acti_v', 'actiplus', 'aero', 
                           'after_eight', 'ahusglass', 'aino', 'al_manhal', 'alacam']

# Empty list to store brands with Instagram accounts
brands_with_instagram = []

# Loop through each brand and check for Instagram account
for brand in brands_instagram_names:
    if check_instagram_account(brand):
        brands_with_instagram.append(brand)

# Print the list of brands with Instagram accounts
print("Brands with Instagram accounts:")
print(brands_with_instagram)
