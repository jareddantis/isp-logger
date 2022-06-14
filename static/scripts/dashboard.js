const $ = (selector) => document.querySelector(selector);

const history_row = (asn, as_name, first_seen, last_seen) => {
    // Turn timestamps into human-readable dates
    const first_obj = new Date(first_seen);
    const last_obj = new Date(last_seen);
    const first_date = first_obj.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    const first_time = first_obj.toLocaleTimeString('en-US');
    const last_date = last_obj.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    const last_time = last_obj.toLocaleTimeString('en-US');

    // Create row
    const row = document.createElement('div');
    row.classList.add('mb-4');
    row.innerHTML = `
        <h3 class="text-3xl mb-2 font-bold">${asn} ${as_name}</h3>
        <p>${first_date} ${first_time} &#8212; ${last_date} ${last_time}</p>
    `;
    return row;
}

window.onload = () => {
    // Create request to ipinfo.io
    fetch('/api/v1/isp')
        .then(response => response.json())
        .then(data => {
            // Display current ISP info
            $('#current-as').innerText = data.now.org;
            $('#current-ip').innerHTML = `${data.now.ip}<br>${data.now.hostname}`;
            $('#current-loc').innerHTML = data.now.location;

            // Create rows for each ISP in history
            for (const item in data.history) {
                const asn = data.history[item].asn;
                const as_name = data.history[item].as_name;
                const first_seen = data.history[item].first_seen;
                const last_seen = data.history[item].last_seen;
                const row = history_row(asn, as_name, first_seen, last_seen);
                $('#history').appendChild(row);
            }
        });
}
