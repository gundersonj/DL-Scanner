function handleScan() {
    const barcode = document.getElementById('barcodeInput').value;
    fetch('/decode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ barcode })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('first_name').value = data.first_name || '';
        document.getElementById('last_name').value = data.last_name || '';
        document.getElementById('dob').value = data.dob || '';
        document.getElementById('license_number').value = data.license_number || '';
        document.getElementById('date_issued').value = data.date_issued || '';
        document.getElementById('expiration_date').value = data.expiration_date || '';
        document.getElementById('address').value = data.address || '';
        document.getElementById('city').value = data.city || '';
        document.getElementById('state').value = data.state || '';
        document.getElementById('zip').value = data.zip || '';
    })
    .catch(error => console.error('Error:', error));
}

function submitForm() {
    const formData = {
        customer_number: document.getElementById('customer_number').value,
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        dob: document.getElementById('dob').value,
        license_number: document.getElementById('license_number').value,
        date_issued: document.getElementById('date_issued').value,
        expiration_date: document.getElementById('expiration_date').value,
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        zip: document.getElementById('zip').value,
    };

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => alert('Data submitted successfully!'))
    .then(location.reload())
    .catch(error => console.error('Error:', error));
}