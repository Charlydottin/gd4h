import requests

def get_datasets():
    r = requests.get("http://localhost:8000/datasets")
    assert r.status_code == 200
    datasets = r.json()
    values = datasets[0].keys()
    assert sorted(values) ==sorted(['state', 'organizations', 'data_domain', 'theme_category', 'qualification_comments', 'nature', 'environment', 'subthematic', 'exposure_factor_category', 'name', 'acronym', 'description', 'has_filter', 'has_search_engine', 'integration_status', 'is_opendata', 'license_name', 'license_type', 'has_restrictions', 'restrictions_comments', 'downloadable', 'broadcast_mode', 'is_geospatial_data', 'geographical_geospatial_coverage', 'geographical_information_level', 'projection_system', 'related_geographical_information', 'has_related_referential', 'year_start', 'year_end', 'year', 'temporal_scale', 'update_frequency', 'automatic_update', 'last_updated', 'format', 'data_format', 'metrics_registered_elements', 'volume', 'measurement_data', 'has_documentation', 'documentation_comments', 'has_missing_data', 'missing_data_comments', 'has_compliance', 'compliance_comments', 'has_pricing', 'pricing_comments', 'contact_type_comments', 'last_inserted', 'last_modification', 'comments', 'related_datasets', 'other_access_points', 'url', '_id'])
    assert len(datasets) == 114

def get_datasets_en():
    r = requests.get("http://localhost:8000/datasets/?lang=en")
    assert r.status_code == 200
    datasets = r.json()
    assert datasets[0]["update_frequency"] == ["Irregular"]
    
    assert sorted(datasets[110].keys()) ==sorted(['state', 'organizations', 'data_domain', 'theme_category', 'qualification_comments', 'nature', 'environment', 'subthematic', 'exposure_factor_category', 'name', 'acronym', 'description', 'has_filter', 'has_search_engine', 'integration_status', 'is_opendata', 'license_name', 'license_type', 'has_restrictions', 'restrictions_comments', 'downloadable', 'broadcast_mode', 'is_geospatial_data', 'geographical_geospatial_coverage', 'geographical_information_level', 'projection_system', 'related_geographical_information', 'has_related_referential', 'year_start', 'year_end', 'year', 'temporal_scale', 'update_frequency', 'automatic_update', 'last_updated', 'format', 'data_format', 'metrics_registered_elements', 'volume', 'measurement_data', 'has_documentation', 'documentation_comments', 'has_missing_data', 'missing_data_comments', 'has_compliance', 'compliance_comments', 'has_pricing', 'pricing_comments', 'contact_type_comments', 'last_inserted', 'last_modification', 'comments', 'related_datasets', 'other_access_points', 'url', '_id'])
    assert len(datasets) ==114

def get_dataset():
    r = requests.get("http://localhost:8000/datasets/61fdb1c4c917bd760bc3f99a")
    assert r.status_code == 200
    dataset = r.json()
    assert dataset["name"] == "Adresses"
    assert sorted(list(dataset.keys())) == sorted(['state', 'organizations', 'data_domain', 'theme_category', 'qualification_comments', 'nature', 'environment', 'subthematic', 'exposure_factor_category', 'name', 'acronym', 'description', 'has_filter', 'has_search_engine', 'integration_status', 'is_opendata', 'license_name', 'license_type', 'has_restrictions', 'restrictions_comments', 'downloadable', 'broadcast_mode', 'is_geospatial_data', 'geographical_geospatial_coverage', 'geographical_information_level', 'projection_system', 'related_geographical_information', 'has_related_referential', 'year_start', 'year_end', 'year', 'temporal_scale', 'update_frequency', 'automatic_update', 'last_updated', 'format', 'data_format', 'metrics_registered_elements', 'volume', 'measurement_data', 'has_documentation', 'documentation_comments', 'has_missing_data', 'missing_data_comments', 'has_compliance', 'compliance_comments', 'has_pricing', 'pricing_comments', 'contact_type_comments', 'last_inserted', 'last_modification', 'comments', 'related_datasets', 'other_access_points', 'url', '_id'])

def get_dataset_en():
    r = requests.get("http://localhost:8000/datasets/61fdb1c4c917bd760bc3f99a/?lang=en")
    assert r.status_code == 200
    dataset = r.json()
    
    assert dataset["name"] == "Adresses"
    assert sorted(list(dataset.keys())) == sorted(['state', 'organizations', 'data_domain', 'theme_category', 'qualification_comments', 'nature', 'environment', 'subthematic', 'exposure_factor_category', 'name', 'acronym', 'description', 'has_filter', 'has_search_engine', 'integration_status', 'is_opendata', 'license_name', 'license_type', 'has_restrictions', 'restrictions_comments', 'downloadable', 'broadcast_mode', 'is_geospatial_data', 'geographical_geospatial_coverage', 'geographical_information_level', 'projection_system', 'related_geographical_information', 'has_related_referential', 'year_start', 'year_end', 'year', 'temporal_scale', 'update_frequency', 'automatic_update', 'last_updated', 'format', 'data_format', 'metrics_registered_elements', 'volume', 'measurement_data', 'has_documentation', 'documentation_comments', 'has_missing_data', 'missing_data_comments', 'has_compliance', 'compliance_comments', 'has_pricing', 'pricing_comments', 'contact_type_comments', 'last_inserted', 'last_modification', 'comments', 'related_datasets', 'other_access_points', 'url', '_id'])

def get_organizations():
    r = requests.get("http://localhost:8000/organizations")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 43
    
def get_organizations_en():
    r = requests.get("http://localhost:8000/organizations/?lang=en")
    assert r.status_code == 200, r.status_code
    items = r.json()
    assert len(items) == 43
    assert items[0]['organization_type'] == 'Association law 1901', items[0]['organization_type']

def get_organization():
    r = requests.get("http://localhost:8000/organizations/61fdb1c2c917bd760bc3f96f")
    assert r.status_code == 200, r.status_code
    item = r.json()
    assert item["url"] == 'http://www.acoucité.org'
    assert item['organization_type'] == 'Association loi 1901'

def get_organization_en():
    r = requests.get("http://localhost:8000/organizations/61fdb1c2c917bd760bc3f96f/?lang=en")
    assert r.status_code == 200
    item = r.json()
    assert item["url"] == 'http://www.acoucité.org'
    assert item['organization_type'] == 'Association law 1901', item['organization_type']

def get_organization_filters():
    r = requests.get("http://localhost:8000/organizations/filters/")
    assert r.status_code == 200, r.status_code
    filters = r.json()
    assert sorted(["name", 'is_controled', "is_multiple", 'is_bool', 'values']) == sorted(filters[0].keys()), filters[0].keys() 
        
def get_dataset_filters():
    r = requests.get("http://localhost:8000/datasets/filters/")
    assert r.status_code == 200, r.status_code
    filters = r.json()
    assert filters[0]["values"][0] == "Agence publique", repr(filters[0]["values"][0])
    assert sorted(["name", 'is_controled', "is_multiple", 'is_bool', 'values']) == sorted(filters[0].keys()), filters[0].keys()

def get_dataset_filters_en():
    r = requests.get("http://localhost:8000/datasets/filters/?lang=en")
    assert r.status_code == 200, r.status_code
    filters = r.json()
    assert sorted(["name", 'is_controled', "is_multiple", 'is_bool', 'values']) == sorted(filters[0].keys()), filters[0].keys()
    assert filters[0]["values"][0] == "Administrative Public Institution", filters[0]["values"][0] 
def search_dataset_001():
    r = requests.get("http://localhost:8000/datasets/search?query=m%C3%A9taux%20lourds&lang=fr")
    assert r.status_code == 200, r.status_code
    response = r.json()
    assert "count" in response
    assert "results" in response
    assert "query" in response
    assert response["query"] == "métaux lourds", response["query"]
    assert response["results"][1]['geographical_information_level'] == ['Station de mesure'], response["results"][1]
def filter_dataset_001():
    data = {"organizations": ["ANSES"]}
    r = requests.post("http://localhost:8000/datasets/filter/", data=data)
    assert r.status_code == 422, r.status_code
    print(r.json())
def filter_dataset_002():
    data = {
        "is_opendata": True,
        "downloadable": True,
        "is_geospatial_data": True
    }
    r = requests.post("http://localhost:8000/datasets/filter/", data=data)
    assert r.status_code == 200, r.status_code
if __name__ == "__main__":
    get_datasets()
    get_datasets_en()
    get_dataset()
    get_dataset_en()
    get_organizations()
    get_organizations_en()
    get_organization()
    get_organization_en()
    get_organization_filters()
    get_dataset_filters()
    get_dataset_filters_en()
    search_dataset_001()
    filter_dataset_001()