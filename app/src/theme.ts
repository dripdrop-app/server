import { createTheme } from '@mui/material/styles';
import { blue, yellow } from '@mui/material/colors';

export default createTheme({
	palette: {
		mode: 'dark',
		primary: {
			main: blue[700],
			dark: blue[900],
		},
		secondary: {
			main: yellow[700],
			dark: yellow[900],
		},
	},
	components: {
		MuiAppBar: {
			styleOverrides: { root: { backgroundColor: blue[900] } },
		},
		MuiListItemIcon: {
			styleOverrides: { root: { color: blue[400] } },
		},
	},
});
