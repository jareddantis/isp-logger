const $ = (selector) => document.querySelector(selector);

const history_row = (as_name, first_seen, last_seen) => {
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
        <h3 class="text-2xl mb-2 font-bold">${as_name}</h3>
        <p class="text-gray-500 text-sm">${first_date} ${first_time} &#8212; ${last_date} ${last_time}</p>
    `;
    return row;
};
const history_legend = (color, as_name) => {
    const doc = new DOMParser().parseFromString(`
        <div class="flex flex-row items-center">
            <div class="w-2 h-2 bg-${color}-500 rounded-full">&nbsp;</div>
            <p class="text-sm text-zinc-500 ml-2">${as_name}</p>
        </div>
    `, 'text/html');
    return doc.firstChild;
};
const colors = 'red orange yellow green blue indigo violet'.split(' ');

window.onload = () => {
    // Create request to ipinfo.io
    fetch('/api/v1/isp')
        .then(response => response.json())
        .then(data => {
            // If no data, display no data
            if (!data.length) {
                $('#current-as').innerText = '(no data)';
                $('#current-ip').innerText = '-';
                $('#current-loc').innerText = '-';
            }

            // Display current ISP info
            const current_isp = data.history[0];
            const current_obj = new Date(current_isp.last_seen);
            const current_date = current_obj.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
            const current_time = current_obj.toLocaleTimeString('en-US');
            $('#current-as').innerText = current_isp.as_name + ' (AS' + current_isp.asn + ')';
            $('#current-ip').innerHTML = current_isp.ip;
            $('#current-loc').innerHTML = current_isp.location;
            $('#current-timestamp').innerText = current_date + ' ' + current_time;

            // Map each AS to a color
            const as_list = data.autonomous_systems;
            const as_colors = {'-1': 'gray'};
            for (const [asn, as_name] of Object.entries(as_list)) {
                const as_color = colors[asn % colors.length];
                as_colors[asn.toString()] = as_color;

                // Create legend item
                const legend_item = history_legend(as_color, as_name);
                $('#history-legend').appendChild(legend_item);
            }

            // Create rows for each ISP in history
            let num_points = 0;
            for (const item in data.history) {
                // Display 'no connection' if ASN is -1
                const asn = data.history[item].asn;
                let as_name = data.history[item].as_name + ' (AS' + asn + ')';
                if (asn === -1) {
                    as_name = 'No internet connection';
                }

                // Display history data
                const first_seen = data.history[item].first_seen;
                let last_seen = data.history[item].last_seen;
                const row = history_row(as_name, first_seen, last_seen);
                $('#history').appendChild(row);

                // Add one data point for every minute
                console.info(first_seen, last_seen);
                while (last_seen > first_seen && num_points < 720) {
                    const point = document.createElement('div')
                    point.classList.add('bg-' + as_colors[asn] + '-500');
                    point.classList.add('md:rounded-full');
                    point.innerHTML = '&nbsp;';
                    $('#history-graph').appendChild(point);
                    last_seen -= 60000;
                    num_points++;
                }
            }

            // Pad points with outlined cells
            while (num_points < 720) {
                const point = document.createElement('div')
                point.classList.add('bg-zinc-300');
                point.classList.add('md:rounded-full');
                point.innerHTML = '&nbsp;';
                $('#history-graph').appendChild(point);
                num_points++;
            }
        });
}
