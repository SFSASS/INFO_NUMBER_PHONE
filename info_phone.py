import os
import sys
import time
import re
import json
import requests
import phonenumbers
from datetime import datetime
from colorama import init, Fore, Style, Back
from bs4 import BeautifulSoup
import webbrowser
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
from phonenumbers import carrier, geocoder, timezone

# Initialize colorama
init(autoreset=True)

class InfoPhone:
    def __init__(self):
        self.phone = ""
        self.country_code = ""
        self.number = ""
        self.phone_info = {
            'valid': False,
            'country': '',
            'carrier': '',
            'timezone': '',
            'national_number': '',
            'international_format': '',
            'region': ''
        }
        self.social_media = {
            "Facebook": {
                "url": "https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0",
                "method": "GET",
                "params": {"phone": ""}
            },
            "Twitter": {
                "url": "https://twitter.com/i/flow/account-recovery",
                "method": "GET"
            },
            "Instagram": {
                "url": "https://www.instagram.com/accounts/password/reset/",
                "method": "GET"
            },
            "Telegram": {
                "url": "https://my.telegram.org/auth",
                "method": "GET"
            },
            "Snapchat": {
                "url": "https://accounts.snapchat.com/accounts/v2/login",
                "method": "GET"
            },
            "TikTok": {
                "url": "https://www.tiktok.com/login/phone-or-email/forgot-password",
                "method": "GET"
            },
            "WhatsApp": {
                "url": "https://www.whatsapp.com/account/delete-my-account",
                "method": "GET"
            },
            "LinkedIn": {
                "url": "https://www.linkedin.com/checkpoint/rp/request-password-reset",
                "method": "GET"
            },
            "VK": {
                "url": "https://vk.com/restore",
                "method": "GET"
            },
            "WeChat": {
                "url": "https://help.wechat.com/account/recover",
                "method": "GET"
            },
            "Careem": {
                "url": "https://www.careem.com/forgot-password",
                "method": "POST",
                "data": {"username": ""},
                "headers": {"Content-Type": "application/json"}
            },
            "Threads": {
                "url": "https://www.threads.net/login/forgot-password",
                "method": "GET"
            },
            "GitHub": {
                "url": "https://github.com/password_reset",
                "method": "POST",
                "data": {"value": ""},
                "params": {"type": "email_or_username"}
            },
            "Gmail": {
                "url": "https://accounts.google.com/signin/v2/identifier",
                "method": "GET",
                "params": {
                    "flowName": "GlifWebSignIn",
                    "flowEntry": "ServiceLogin"
                }
            },
            "Hotmail/Outlook": {
                "url": "https://login.live.com/GetCredentialType.srf",
                "method": "POST",
                "json": {
                    "username": "",
                    "isOtherIdpSupported": False,
                    "checkPhones": True,
                    "isRemoteNGCSupported": True,
                    "isCookieBannerShown": False,
                    "isFidoSupported": False,
                    "originalRequest": ""
                },
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            }
        }
        self.results = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def print_banner(self):
        banner = f"""
{Fore.GREEN}
  ██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗     
  ██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝     
  ██████╔╝███████║██║   ██║██╔██╗ ██║█████╗       
  ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝       
  ██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗     
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝     
                                                  
  ██████╗ ██████╗ ███╗   ██╗███████╗�█████╗ ██╗  
 ██╔════╝██╔═══██╗████╗  ██║██╔════╝██╔══██╗██║  
 ██║     ██║   ██║██╔██╗ ██║█████╗  ██████╔╝██║  
 ██║     ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗╚═╝  
 ╚██████╗╚██████╔╝██║ ╚████║███████╗██║  ██║██╗  
  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  
                                                  
  ███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗       
  ██╔════╝╚██╗██╔╝██╔════╝██╔═══██╗██╔════╝       
 █████╗   ╚███╔╝ ██║     ██║   ██║███████╗       
  ██╔══╝   ██╔██╗ ██║     ██║   ██║╚════██║       
  ███████╗██╔╝ ██╗╚██████╗╚██████╔╝███████║       
  ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝       

{Style.RESET_ALL}"""
        print(banner)

    def validate_phone(self, phone):
        """Validate and parse phone number."""
        try:
            # Parse the phone number
            parsed = phonenumbers.parse(phone)
            
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            
            # Extract phone information
            self.phone_info.update({
                'valid': True,
                'country': geocoder.country_name_for_number(parsed, 'en') or 'Unknown',
                'carrier': carrier.name_for_number(parsed, 'en') or 'Unknown',
                'timezone': ', '.join(timezone.time_zones_for_number(parsed)) or 'Unknown',
                'national_number': parsed.national_number,
                'international_format': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'region': geocoder.description_for_number(parsed, 'en') or 'Unknown'
            })
            
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise ValueError("Invalid phone number format. Please use format: +[country code][number]") from e

    def get_phone_number(self):
        """Get and validate phone number input from user."""
        while True:
            try:
                print(f"\n{Fore.RED}[*] Enter phone number with country code (e.g., +1234567890): {Style.RESET_ALL}")
                phone = input(f"{Fore.RED}> {Style.RESET_ALL}").strip()
                self.phone = self.validate_phone(phone)
                
                # Extract country code and number
                match = re.match(r'\+(\d{1,3})(\d+)', self.phone)
                if match:
                    self.country_code = match.group(1)
                    self.number = match.group(2)
                
                return self.phone
                
            except ValueError as e:
                print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
                return None

    def check_single_platform(self, platform, data):
        """Check a single social media platform for the phone number."""
        try:
            print(f"{Fore.CYAN}[*] Checking {platform}...{Style.RESET_ALL}", end='\r')
            
            # Prepare request data
            url = data['url']
            method = data.get('method', 'GET').upper()
            headers = data.get('headers', {})
            
            # Prepare request parameters based on platform
            request_params = data.get('params', {})
            request_data = data.get('data', {})
            json_data = data.get('json')
            
            # Update phone/email in request data if needed
            if platform.lower() in ['careem']:
                request_data['username'] = self.phone
            elif platform.lower() in ['github']:
                request_data['value'] = self.phone
            elif platform.lower() in ['hotmail/outlook']:
                json_data['username'] = self.phone
            
            # Build the full URL with parameters
            if request_params:
                full_url = f"{url}?{requests.compat.urlencode(request_params, doseq=True)}"
            else:
                full_url = url
            
            # Make the request
            try:
                request_kwargs = {
                    'url': url,
                    'headers': {**self.session.headers, **headers},
                    'timeout': 10,
                    'allow_redirects': True
                }
                
                if method == 'POST':
                    if json_data is not None:
                        request_kwargs['json'] = json_data
                    if request_data:
                        request_kwargs['data'] = request_data
                    if request_params:
                        request_kwargs['params'] = request_params
                    
                    response = self.session.post(**request_kwargs)
                else:  # GET
                    if request_params:
                        request_kwargs['params'] = request_params
                    response = self.session.get(**request_kwargs)
                
                # Check response for indicators of account existence
                found = False
                status_code = response.status_code
                
                # Platform-specific checks
                if status_code == 200:
                    text = response.text.lower()
                    
                    # Common patterns that might indicate account existence
                    patterns = [
                        'account', 'user', 'profile', 'phone', 'number',
                        'forgot', 'password', 'reset', 'recover', 'sign in',
                        'log in', 'verify', 'code', 'otp'
                    ]
                    
                    # Platform-specific checks
                    if platform.lower() == 'careem':
                        found = 'forgot-password' in response.url and 'login' not in response.url
                    elif platform.lower() == 'github':
                        found = 'password_reset' in response.url and 'verify' not in response.url
                    elif platform.lower() in ['gmail', 'hotmail/outlook']:
                        found = any(p in text for p in ['account', 'sign in', 'log in'])
                    else:
                        found = any(p in text for p in patterns)
                
                # Special case for successful API responses
                if status_code in [200, 201, 202] and json_data is not None:
                    try:
                        json_response = response.json()
                        if platform.lower() == 'hotmail/outlook':
                            found = json_response.get('IfExistsResult') in [0, 1]  # 0 = Account exists, 1 = Account doesn't exist
                    except:
                        pass
                
                # Store result
                self.results[platform] = {
                    'found': found,
                    'url': full_url,
                    'status_code': response.status_code,
                    'checked_at': datetime.now().isoformat()
                }
                
                # Print result
                status = f"{Fore.GREEN}Found{Style.RESET_ALL}" if found else f"{Fore.RED}Not Found{Style.RESET_ALL}"
                print(f"{' ' * 50}", end='\r')
                print(f"{Fore.GREEN}[+] {platform}: {status} ({response.status_code}){Style.RESET_ALL}")
                
            except requests.RequestException as e:
                print(f"{Fore.YELLOW}[!] Network error checking {platform}: {str(e)}{Style.RESET_ALL}")
                self.results[platform] = {
                    'found': False,
                    'error': str(e),
                    'url': full_url,
                    'checked_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"{Fore.RED}[!] Error checking {platform}: {str(e)}{Style.RESET_ALL}")
            self.results[platform] = {
                'found': False,
                'error': str(e),
                'url': full_url if 'full_url' in locals() else url,
                'checked_at': datetime.now().isoformat()
            }

    def show_phone_info(self):
        """Display phone number information."""
        if not self.phone_info['valid']:
            return
            
        print(f"\n{Fore.RED}=== PHONE NUMBER INFORMATION ==={Style.RESET_ALL}")
        
        info = [
            ("Phone Number", self.phone_info['international_format']),
            ("Country", self.phone_info['country']),
            ("Region", self.phone_info['region']),
            ("Carrier", self.phone_info['carrier']),
            ("Timezone", self.phone_info['timezone'])
        ]
        
        for label, value in info:
            print(f"{Fore.RED}[*] {Fore.WHITE}{label + ':':<15} {value}")

    def check_social_media(self):
        """Check all social media platforms for the phone number."""
        # Display phone information first
        self.show_phone_info()
        
        print(f"\n{Fore.RED}[*] Searching for social media accounts...{Style.RESET_ALL}")
        print(f"{Fore.RED}[*] Phone: {self.phone_info['international_format']}{Style.RESET_ALL}\n")
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for platform, data in self.social_media.items():
                future = executor.submit(self.check_single_platform, platform, data)
                futures.append(future)
                time.sleep(0.2)  # Small delay between starting tasks
                
            # Wait for all tasks to complete
            for future in futures:
                future.result()

    def show_results(self):
        """Display the search results in a simplified format."""
        # Display the results
        print(f"\n{Fore.RED}=== SEARCH RESULTS ==={Style.RESET_ALL}")
        
        # Phone info
        print(f"\n{Fore.RED}Phone Information:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Full Number: {self.phone}")
        print(f"{Fore.WHITE}Country Code: +{self.country_code}")
        print(f"{Fore.WHITE}Local Number: {self.number}")
        
        # Results summary
        found_count = sum(1 for r in self.results.values() if r.get('found'))
        total = len(self.results)
        
        print(f"\n{Fore.RED}Search Summary:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Platforms Checked: {total}")
        print(f"{Fore.GREEN}Accounts Found: {found_count}")
        print(f"{Fore.RED}Accounts Not Found: {total - found_count}")
        
        # Detailed results
        print(f"\n{Fore.RED}Detailed Results:{Style.RESET_ALL}")
        print(f"{'=' * 60}")
        print(f"{'Platform'.ljust(20)} {'Status'}")
        print(f"{'=' * 60}")
        
        for platform, data in sorted(self.results.items()):
            status = f"{Fore.GREEN}Found" if data.get('found') else f"{Fore.RED}Not Found"
            print(f"{Fore.WHITE}{platform.ljust(20)} {status}{Style.RESET_ALL}")
            
            if 'error' in data:
                error_msg = data.get('error', '')[:50]
                print(f"   {Fore.YELLOW}Error: {error_msg}...{Style.RESET_ALL}")
        
        # Display clickable links for found accounts
        found_accounts = {k: v for k, v in self.results.items() if v.get('found')}
        if found_accounts:
            print(f"\n{Fore.GREEN}[+] Found accounts - Clickable Links:{Style.RESET_ALL}")
            for platform, data in found_accounts.items():
                print(f"{Fore.WHITE}• {platform}: {data['url']}{Style.RESET_ALL}")

    def save_results(self):
        """Save the search results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phone_results_{self.phone.replace('+', '')}_{timestamp}.json"
        
        # Prepare data for JSON
        result_data = {
            "search_info": {
                "phone_number": self.phone,
                "country_code": self.country_code,
                "local_number": self.number,
                "search_timestamp": datetime.now().isoformat(),
                "platforms_checked": len(self.results)
            },
            "results": self.results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n{Fore.GREEN}[*] Results saved to {filename}{Style.RESET_ALL}")
            return filename
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error saving results: {str(e)}{Style.RESET_ALL}")
            return None

    def run(self):
        """Run the main application."""
        try:
            # Clear screen and show banner
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_banner()
            
            # Get phone number
            if not self.get_phone_number():
                print(f"{Fore.RED}[!] Invalid phone number. Exiting...{Style.RESET_ALL}")
                return
            
            # Start search
            start_time = time.time()
            self.check_social_media()
            
            # Show and save results
            self.show_results()
            result_file = self.save_results()
            
            # Show completion message
            elapsed = time.time() - start_time
            print(f"\n{Fore.GREEN}[*] Search completed in {elapsed:.2f} seconds{Style.RESET_ALL}")
            if result_file:
                print(f"{Fore.CYAN}[*] Full results saved to: {result_file}{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[*] Note: This tool is for educational purposes only.{Style.RESET_ALL}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Search interrupted by user.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}[!] An error occurred: {str(e)}{Style.RESET_ALL}")
            if 'self.results' in locals() and self.results:
                self.save_results()  # Try to save partial results

if __name__ == "__main__":
    try:
        # Check if running in a terminal that supports colors
        if not sys.stdout.isatty():
            print("Warning: Not running in a terminal. Some features may not work correctly.")
        
        # Initialize and run the tool
        tool = InfoPhone()
        tool.run()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Process interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except ImportError as e:
        print(f"\n{Fore.RED}[!] Missing required module: {str(e)}{Style.RESET_ALL}")
        print(f"Please install the required packages using: {Fore.CYAN}pip install -r requirements.txt{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[!] An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
