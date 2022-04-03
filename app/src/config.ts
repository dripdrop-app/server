const isProd = process.env.NODE_ENV === 'production';
const protocol = isProd ? 'wss' : 'ws';
const server_domain = isProd ? 'dripdrop.icu' : 'localhost:5000';

export const buildWebsocketURL = (endpoint: string) => `${protocol}://${server_domain}${endpoint}`;
