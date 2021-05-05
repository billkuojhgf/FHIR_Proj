from fhirpy import SyncFHIRClient


def main():
    client = SyncFHIRClient(
        'http://localhost:5555/fhir'
    )

    resources = client.resource('Patient')
    resources = resources.search(gender='male').limit(100).sort('id')
    patients = resources.fetch()
    print(patients)
