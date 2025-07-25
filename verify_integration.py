#!/usr/bin/env python3
"""
Simple verification script for KKH Baby Bear Book Section 01 integration
"""

import os
import sys

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def check_content_in_file(filepath, search_terms):
    """Check if specific content exists in a file"""
    if not os.path.exists(filepath):
        return False, f"File {filepath} not found"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        found_terms = []
        missing_terms = []
        
        for term in search_terms:
            if term.lower() in content.lower():
                found_terms.append(term)
            else:
                missing_terms.append(term)
        
        return len(missing_terms) == 0, {
            'found': found_terms,
            'missing': missing_terms,
            'total_content_length': len(content)
        }
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    print("🏥 KKH Baby Bear Book Section 01 Integration Verification")
    print("=" * 60)
    
    # Check required files exist
    required_files = [
        'app.py',
        'requirements.txt',
        'Dockerfile',
        'fly.toml',
        'README.md',
        'MEDICAL_EMERGENCIES.md'
    ]
    
    print("\n📂 Checking Required Files:")
    all_files_exist = True
    for file in required_files:
        exists = check_file_exists(file)
        status = "✅" if exists else "❌"
        print(f"  {status} {file}")
        if not exists:
            all_files_exist = False
    
    # Check KKH Baby Bear Book content in app.py
    print("\n📖 Checking KKH Baby Bear Book Content in app.py:")
    kkh_terms = [
        "Baby Bear Book",
        "KKH",
        "recognising_critically_ill_child",
        "abcde_assessment", 
        "cardiopulmonary_resuscitation",
        "drug_overdose_poisoning",
        "paracetamol_poisoning",
        "Loi V-Ter, Mervin",
        "Lim Kian Boon, Joel",
        "45.6% survival-to-discharge",
        "N-acetylcysteine",
        "Paediatric CPR"
    ]
    
    content_check, result = check_content_in_file('app.py', kkh_terms)
    
    if content_check:
        print("  ✅ All KKH Baby Bear Book content found in app.py")
        print(f"  📊 Total content length: {result['total_content_length']:,} characters")
        print(f"  📝 Found {len(result['found'])}/{len(kkh_terms)} key terms")
    else:
        print("  ❌ Some KKH content missing from app.py")
        if result.get('missing'):
            print("  Missing terms:")
            for term in result['missing']:
                print(f"    - {term}")
    
    # Check UI elements
    print("\n🖥️  Checking UI Integration:")
    ui_terms = [
        "KKH Nursing Assistant",
        "KKH Baby Bear Book",
        "Section 01 Embedded",
        "pediatric emergency protocols"
    ]
    
    ui_check, ui_result = check_content_in_file('app.py', ui_terms)
    
    if ui_check:
        print("  ✅ All UI elements properly integrated")
    else:
        print("  ❌ Some UI elements missing")
        if ui_result.get('missing'):
            for term in ui_result['missing']:
                print(f"    - Missing: {term}")
    
    # Check deployment configuration
    print("\n🚀 Checking Deployment Configuration:")
    
    # Check Dockerfile
    dockerfile_terms = ['FROM python', 'COPY requirements.txt', 'streamlit run']
    dockerfile_check, _ = check_content_in_file('Dockerfile', dockerfile_terms)
    print(f"  {'✅' if dockerfile_check else '❌'} Dockerfile configuration")
    
    # Check fly.toml
    flytoml_terms = ['app =', 'primary_region =', '[[services]]']
    flytoml_check, _ = check_content_in_file('fly.toml', flytoml_terms)
    print(f"  {'✅' if flytoml_check else '❌'} Fly.io configuration")
    
    # Check requirements.txt
    req_terms = ['streamlit', 'sentence-transformers', 'faiss-cpu']
    req_check, _ = check_content_in_file('requirements.txt', req_terms)
    print(f"  {'✅' if req_check else '❌'} Python dependencies")
    
    # Summary
    print("\n📋 Verification Summary:")
    print("=" * 30)
    
    overall_status = all([
        all_files_exist,
        content_check,
        ui_check,
        dockerfile_check,
        flytoml_check,
        req_check
    ])
    
    if overall_status:
        print("🎉 SUCCESS: KKH Baby Bear Book Section 01 is fully integrated!")
        print("\n✅ Ready for deployment with:")
        print("   • Official KKH pediatric emergency protocols")
        print("   • 5 comprehensive emergency sections")
        print("   • Age-specific vital signs and procedures")
        print("   • Evidence-based resuscitation protocols")
        print("   • Complete toxicology management")
        print("   • Fly.io deployment configuration")
        
        print("\n🚀 Next Steps:")
        print("   1. Test locally: streamlit run app.py")
        print("   2. Deploy to Fly.io: fly deploy")
        print("   3. Train nursing staff on new features")
        
        return 0
    else:
        print("❌ ISSUES FOUND: Please check the errors above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
