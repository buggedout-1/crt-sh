import requests
import argparse
import re
import os

# Function to fetch subdomains from crt.sh
def get_subdomains(domain):
    url = f"https://crt.sh/?q={domain}&output=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        subdomains = set()  # Use a set to avoid duplicates
        for cert in response.json():
            # Extract the subject names from the certificate data
            if 'commonName' in cert:
                subdomains.add(cert['commonName'])
            if 'name_value' in cert:
                for name in cert['name_value'].split('\n'):
                    subdomains.add(name)
        return list(subdomains)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

# Function to filter and only return valid subdomains of the form "*.domain.com" or "subdomain.domain.com"
def filter_subdomains(subdomains, domain):
    # Regular expression to match valid subdomains
    pattern = re.compile(r'([a-zA-Z0-9-]+\.)+' + re.escape(domain) + r'$', re.IGNORECASE)
    filtered_subdomains = [subdomain for subdomain in subdomains if pattern.match(subdomain)]
    return filtered_subdomains

# Function to process a list of domains
def process_domain_list(domain_list, output_file):
    all_subdomains = []
    for domain in domain_list:
        domain = domain.strip()
        if domain:
            print(f"Fetching subdomains for {domain}...")
            subdomains = get_subdomains(domain)
            filtered_subdomains = filter_subdomains(subdomains, domain)
            all_subdomains.extend(filtered_subdomains)
            # Optionally write each domain's results to the output file
            if output_file:
                with open(output_file, "a") as f:
                    for subdomain in filtered_subdomains:
                        f.write(f"{subdomain}\n")
    return all_subdomains

# Main function to parse the argument and execute the tool
def main():
    parser = argparse.ArgumentParser(description="Fetch subdomains of a domain from crt.sh")
    parser.add_argument("-d", "--domain", help="Single domain to fetch subdomains for")
    parser.add_argument("-l", "--list", help="File containing a list of domains to fetch subdomains for")
    parser.add_argument("-o", "--output", help="Output file to save subdomains")
    
    args = parser.parse_args()
    
    if args.domain:
        subdomains = get_subdomains(args.domain)
        filtered_subdomains = filter_subdomains(subdomains, args.domain)
        if args.output:
            with open(args.output, "w") as f:  # Open the file in write mode to overwrite
                for subdomain in filtered_subdomains:
                    f.write(f"{subdomain}\n")
        else:
            print(f"Subdomains of {args.domain}:")
            for subdomain in filtered_subdomains:
                print(subdomain)
    
    elif args.list:
        if not os.path.exists(args.list):
            print(f"Error: The file {args.list} does not exist.")
            return
        
        with open(args.list, "r") as f:
            domain_list = f.readlines()
        
        all_subdomains = process_domain_list(domain_list, args.output)
        if all_subdomains:
            print(f"\nTotal subdomains found:")
            for subdomain in set(all_subdomains):  # Ensure uniqueness
                print(subdomain)
        else:
            print(f"No subdomains found for the domains in {args.list}.")
    else:
        print("Please provide a domain with -d or a file with -l.")

if __name__ == "__main__":
    main()
