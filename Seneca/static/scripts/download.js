document.addEventListener('DOMContentLoaded', function (evemt) {
    console.log("Calling download")
    const path = window.location.pathname;
    console.log(path)

    const parts = path.split('/');

    // The last two parts will be order_id and download_url
    const order_id = parts[parts.length - 2].split('=')[1]; // Extract the value after '='
    const download_url = parts[parts.length - 1];

    console.log('Order ID:', order_id);
    console.log('Download URL:', download_url);
    if (order_id && download_url) {
        const downloadUrl = `/validate-download?order_id=${order_id}&token_download_url=${download_url}`;
        window.location.href = downloadUrl;
    }
})