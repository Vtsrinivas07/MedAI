"""
Test script for Medical Image Diagnosis API
Tests the /api/diagnose endpoint with a sample image
"""

import requests
import sys
from PIL import Image
import io

API_BASE = "http://localhost:8000"


def create_test_image():
    """Create a simple test image (224x224 RGB)"""
    img = Image.new('RGB', (224, 224), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


def test_diagnose_endpoint(token: str, image_path: str = None, modality: str = "skin"):
    """
    Test the /api/diagnose endpoint
    
    Args:
        token: JWT auth token
        image_path: Path to image file (optional, creates test image if None)
    """
    print("🧪 Testing /api/diagnose endpoint...")
    print(f"   API: {API_BASE}")
    
    # Prepare image
    if image_path:
        print(f"   Using image: {image_path}")
        with open(image_path, 'rb') as f:
            files = {'image': (image_path, f, 'image/jpeg')}
            data = {
                'symptoms': 'Red, itchy patches on skin',
                'modality': modality
            }
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.post(
                f"{API_BASE}/api/diagnose",
                files=files,
                data=data,
                headers=headers
            )
    else:
        print("   Using test image (auto-generated)")
        test_img = create_test_image()
        files = {'image': ('test.png', test_img, 'image/png')}
        data = {
            'symptoms': 'Testing the API endpoint',
            'modality': modality
        }
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(
            f"{API_BASE}/api/diagnose",
            files=files,
            data=data,
            headers=headers
        )
    
    # Check response
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success'):
            data = result['data']
            print("\n✅ Diagnosis Successful!")
            print(f"   Modality: {data.get('modality', 'unknown')}")
            print(f"   Disease: {data['disease']}")
            print(f"   Confidence: {data['confidence']:.2%}")
            print(f"   Meets Threshold: {data['meets_threshold']}")
            print(f"   Doctor: {data['doctor']['specialty']}")
            print(f"   Urgency: {data['doctor']['urgency']}")
            
            print("\n📋 Top Predictions:")
            for i, pred in enumerate(data['all_predictions'][:3], 1):
                print(f"   {i}. {pred['disease']}: {pred['confidence']:.2%}")
            
            print("\n💊 Treatment Suggestions:")
            for med in data['treatment']['medications'][:3]:
                print(f"   - {med}")
            
            print("\n🩺 Explanation (first 200 chars):")
            print(f"   {data['explanation'][:200]}...")
            
        else:
            print("❌ Request failed (success=false)")
            print(result)
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(response.text)


def test_model_info_endpoint(token: str, modality: str = "skin"):
    """Test the /api/diagnose/model-info endpoint"""
    print("\n🧪 Testing /api/diagnose/model-info endpoint...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f"{API_BASE}/api/diagnose/model-info",
        params={"modality": modality},
        headers=headers
    )
    
    print(f"📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result['data']
            print("\n✅ Model Info Retrieved!")
            print(f"   Model: {data['model_name']}")
            print(f"   Modality: {data.get('modality', 'unknown')}")
            print(f"   Classes: {data['num_classes']}")
            print(f"   Loaded: {data['model_loaded']}")
            print(f"   Device: {data['device']}")
            print(f"   Input Size: {data['input_size']}")
            print(f"   Threshold: {data['confidence_threshold']}")
            print(f"\n   Disease Classes:")
            for cls in data['disease_classes']:
                print(f"      - {cls}")
        else:
            print("❌ Request failed")
            print(result)
    else:
        print(f"❌ Request failed with status {response.status_code}")
        print(response.text)


def login(email: str, password: str):
    """Login and get JWT token"""
    print(f"🔐 Logging in as {email}...")
    
    response = requests.post(
        f"{API_BASE}/api/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            token = result['data']['access_token']
            print("✅ Login successful!")
            return token
        else:
            print("❌ Login failed")
            print(result)
            return None
    else:
        print(f"❌ Login failed with status {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Medical Image Diagnosis API Test")
    print("=" * 60)
    
    # Get credentials
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
        image_path = sys.argv[3] if len(sys.argv) > 3 else None
        modality = sys.argv[4] if len(sys.argv) > 4 else "skin"
    else:
        print("\nUsage:")
        print("  python test_diagnosis_api.py <email> <password> [image_path]")
        print("\nExample:")
        print("  python test_diagnosis_api.py test@example.com password123")
        print("  python test_diagnosis_api.py test@example.com password123 skin_image.jpg")
        print("  python test_diagnosis_api.py test@example.com password123 skin_image.jpg chest")
        print("\nℹ️  If no image provided, a test image will be generated")
        sys.exit(1)
    
    # Login
    token = login(email, password)
    if not token:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Test model info endpoint
    test_model_info_endpoint(token, modality=modality)
    
    print("\n" + "=" * 60)
    
    # Test diagnose endpoint
    test_diagnose_endpoint(token, image_path, modality=modality)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
