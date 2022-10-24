import { createTheme } from '@mui/material/styles';
import { blue } from '@mui/material/colors';
import { PaletteMode } from '@mui/material';

export const createCustomTheme = (mode: PaletteMode) =>
	createTheme({
		palette: {
			mode,
			primary: {
				main: blue[500],
			},
		},
		components: {
			MuiAppBar: {
				styleOverrides: { root: { backgroundColor: mode === 'dark' ? blue[900] : blue[700], borderRadius: 0 } },
			},
			MuiListItemIcon: {
				styleOverrides: { root: { color: blue[500] } },
			},
			MuiLink: {
				styleOverrides: {
					root: {
						color: 'white',
						textDecoration: 'none',
						'&:hover': {
							textDecoration: 'underline',
						},
					},
				},
			},
		},
	});
