let server_domain = '';

if (process.env.NODE_ENV === 'production') {
    server_domain = 'dripdrop.com';
} else {
    server_domain = 'localhost:5000';
}

export {
    server_domain
}