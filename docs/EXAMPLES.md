# SF Express API - Usage Guide

This guide shows you how to use the SF Express Locations API through the web dashboard and API endpoints.

## Quick Start (Web Dashboard)

### 1. Start the Server

```bash
uv run python manage.py runserver
```

The application will be available at `http://localhost:8000/`

### 2. Register an Account

1. Open your browser and go to `http://localhost:8000/`
2. Click "Register" in the navigation
3. Fill in your details:
   - Username
   - Email
   - Password
4. Click "Register"
5. You'll receive 100 free credits automatically!

### 3. Login

1. Click "Login" in the navigation
2. Enter your username and password
3. Click "Login"
4. You'll be redirected to your dashboard

### 4. Create an API Key

From your dashboard:

1. Find the "API Keys" section
2. Enter a descriptive name for your key (e.g., "Production Key", "Test Key")
3. Click "Create API Key"
4. Copy the generated API key - you'll need it for API requests!

### 5. Use the API

Now you can use your API key to query SF Express locations:

```bash
curl -X GET "http://localhost:8000/api/locations" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Dashboard Features

### View Your Credits

Your dashboard shows:
- **Available Credits**: Current credit balance
- **Total Earned**: All credits you've received
- **Total Spent**: Credits used for API calls
- **Active API Keys**: Number of active API keys

### Manage API Keys

- **Create**: Add new API keys with custom names
- **View**: See all your API keys with their creation dates and last used times
- **Delete**: Remove API keys you no longer need

### Transaction History

Monitor your API usage:
- See each API call and its cost
- Track credit purchases and adjustments
- View balance after each transaction

## API Usage Examples

### Basic Request

Get all locations:

```bash
curl -X GET "http://localhost:8000/api/locations" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Response:
```json
{
  "count": 10,
  "locations": [...],
  "credits_used": 5,
  "credits_remaining": 95
}
```

### Filter by Type (Lockers Only)

```bash
curl -X GET "http://localhost:8000/api/locations?type=LOCKER" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Filter by Type (Shops Only)

```bash
curl -X GET "http://localhost:8000/api/locations?type=SHOP" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Filter by District

```bash
curl -X GET "http://localhost:8000/api/locations?district=Central" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Search by Name

```bash
curl -X GET "http://localhost:8000/api/locations?search=Causeway" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Combined Filters

```bash
curl -X GET "http://localhost:8000/api/locations?type=LOCKER&district=Wan%20Chai" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Python Integration

### Simple Example

```python
import requests

BASE_URL = "http://localhost:8000/api"
API_KEY = "your-api-key-here"  # Get this from your dashboard

headers = {"Authorization": f"Bearer {API_KEY}"}

# Get all locations
response = requests.get(f"{BASE_URL}/locations", headers=headers)
data = response.json()

print(f"Found {data['count']} locations")
print(f"Credits used: {data['credits_used']}")
print(f"Credits remaining: {data['credits_remaining']}")

# Print location details
for location in data['locations']:
    print(f"- {location['name']} ({location['location_type']})")
    print(f"  Address: {location['address']}")
    print(f"  District: {location['district']}")
    print(f"  Phone: {location['phone']}")
    print()
```

### With Error Handling

```python
import requests

BASE_URL = "http://localhost:8000/api"
API_KEY = "your-api-key-here"

def get_locations(location_type=None, district=None, search=None):
    """
    Get SF Express locations with optional filters
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {}

    if location_type:
        params['type'] = location_type
    if district:
        params['district'] = district
    if search:
        params['search'] = search

    try:
        response = requests.get(
            f"{BASE_URL}/locations",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Error: Invalid or missing API key")
        elif response.status_code == 402:
            print("Error: Insufficient credits")
        else:
            print(f"HTTP Error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage examples
print("All Lockers:")
data = get_locations(location_type='LOCKER')
if data:
    for loc in data['locations']:
        print(f"- {loc['name']}")

print("\nShops in Central:")
data = get_locations(location_type='SHOP', district='Central')
if data:
    for loc in data['locations']:
        print(f"- {loc['name']}")
```

### Class-Based Wrapper

```python
import requests

class SFExpressAPI:
    def __init__(self, api_key, base_url="http://localhost:8000/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_locations(self, location_type=None, district=None, search=None):
        """Get locations with optional filters"""
        params = {}
        if location_type:
            params['type'] = location_type.upper()
        if district:
            params['district'] = district
        if search:
            params['search'] = search

        response = requests.get(
            f"{self.base_url}/locations",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_all_lockers(self):
        """Get all locker locations"""
        return self.get_locations(location_type='LOCKER')

    def get_all_shops(self):
        """Get all shop locations"""
        return self.get_locations(location_type='SHOP')

    def search(self, query):
        """Search locations by name"""
        return self.get_locations(search=query)

# Usage
api = SFExpressAPI("your-api-key-here")

# Get all lockers
result = api.get_all_lockers()
print(f"Found {result['count']} lockers")
print(f"Credits remaining: {result['credits_remaining']}")

# Search for specific location
result = api.search("Causeway")
for location in result['locations']:
    print(location['name'])
```

## JavaScript Integration

### Using Fetch API

```javascript
const BASE_URL = 'http://localhost:8000/api';
const API_KEY = 'your-api-key-here';  // Get this from your dashboard

async function getLocations(filters = {}) {
    const params = new URLSearchParams(filters);
    const url = `${BASE_URL}/locations?${params}`;

    try {
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${API_KEY}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log(`Found ${data.count} locations`);
        console.log(`Credits remaining: ${data.credits_remaining}`);
        return data;
    } catch (error) {
        console.error('Error fetching locations:', error);
    }
}

// Usage examples
getLocations({ type: 'LOCKER' });
getLocations({ district: 'Central' });
getLocations({ type: 'SHOP', district: 'Wan Chai' });
```

### Using Axios

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api';
const API_KEY = 'your-api-key-here';

const client = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Authorization': `Bearer ${API_KEY}`
    }
});

async function getLocations(params = {}) {
    try {
        const response = await client.get('/locations', { params });
        console.log(`Found ${response.data.count} locations`);
        console.log(`Credits remaining: ${response.data.credits_remaining}`);
        return response.data;
    } catch (error) {
        if (error.response) {
            console.error(`Error ${error.response.status}:`, error.response.data);
        } else {
            console.error('Error:', error.message);
        }
    }
}

// Usage
(async () => {
    // Get all lockers
    await getLocations({ type: 'LOCKER' });

    // Get shops in Central
    await getLocations({ type: 'SHOP', district: 'Central' });

    // Search by name
    await getLocations({ search: 'Causeway' });
})();
```

## Error Responses

### Missing or Invalid API Key

```json
{
  "error": "Authentication required",
  "message": "Missing Authorization header"
}
```

```json
{
  "error": "Invalid API key",
  "message": "The provided API key is invalid or inactive"
}
```

### Insufficient Credits

```json
{
  "error": "Insufficient credits",
  "required": 5,
  "available": 2
}
```

## Tips

1. **Keep your API key secure**: Never commit it to version control
2. **Use environment variables**: Store your API key in environment variables
3. **Monitor your credits**: Check your dashboard regularly to track usage
4. **Create multiple keys**: Use different keys for different applications
5. **Delete unused keys**: Remove API keys you're no longer using for better security

## Support

If you encounter any issues:
1. Check your API key is correct and active
2. Verify you have sufficient credits
3. Ensure the Authorization header is properly formatted
4. Check the admin panel for detailed logs
