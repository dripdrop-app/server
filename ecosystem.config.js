module.exports = {
	apps: [
		{
			name: 'server',
			cmd: 'gunicorn -b :5000 -w 2 -k uvicorn.workers.UvicornWorker server.app:app',
			autorestart: true,
			instances: 1,
			env: {
				ENV: 'development',
			},
			env_production: {
				ENV: 'production',
			},
		},
		{
			name: 'worker',
			cmd: 'dotenv -f .env run python worker.py',
			autorestart: true,
			instances: 1,
		},
	],
};
