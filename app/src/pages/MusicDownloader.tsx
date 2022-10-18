import { useState } from 'react';
import { Container, Stack, Box, Typography, TextField, Switch, InputAdornment, Button, Paper } from '@mui/material';
import MusicForm from '../components/Music/MusicForm';
import JobList from '../components/Music/JobList';

const MusicDownloader = () => {
	const [form, setForm] = useState({
		youtubeUrl: '',
		file: null,
		artworkUrl: '',
		title: '',
		artist: '',
		album: '',
		grouping: '',
	});
	const [checked, setChecked] = useState(false);

	return (
		<Container sx={{ paddingY: 2 }}>
			<Box>
				<Typography variant="h4">Music Downloader / Converter</Typography>
				<Stack component="form" paddingY={4} paddingX={2} spacing={4}>
					<Stack
						direction="row"
						alignItems="center"
						spacing={{
							xs: 0,
							md: 2,
						}}
						flexWrap={{
							xs: 'wrap',
							md: 'nowrap',
						}}
					>
						<TextField label="YouTube URL" variant="standard" fullWidth disabled={checked} />
						<Switch checked={checked} onChange={(e, checked) => setChecked(checked)} />
						<TextField
							label="Filename"
							variant="standard"
							InputProps={{
								endAdornment: (
									<InputAdornment position="end">
										<Button variant="contained" disabled={!checked}>
											Browse
										</Button>
									</InputAdornment>
								),
							}}
							fullWidth
							disabled
						/>
					</Stack>
					<Stack
						direction="row"
						alignItems="center"
						spacing={{
							xs: 0,
							md: 2,
						}}
						flexWrap={{
							xs: 'wrap',
							md: 'nowrap',
						}}
					>
						<Paper variant="outlined">
							<img
								alt="blank"
								width="100%"
								src="https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/blank_image.jpeg"
							/>
						</Paper>
						<Stack
							direction="column"
							width={{
								xs: '100%',
								md: '50%',
							}}
						>
							<TextField label="Artwork URL" variant="standard" fullWidth />
							<TextField label="Resolved Artwork URL" variant="standard" fullWidth disabled />
						</Stack>
					</Stack>
					<Stack
						direction="row"
						justifyContent="space-around"
						spacing={{
							xs: 0,
							md: 2,
						}}
						flexWrap={{
							xs: 'wrap',
							md: 'nowrap',
						}}
					>
						<TextField label="Title" variant="standard" fullWidth />
						<TextField label="Artist" variant="standard" fullWidth />
						<TextField label="Album" variant="standard" fullWidth />
						<TextField label="Grouping" variant="standard" fullWidth />
					</Stack>
					<Stack
						direction="row"
						justifyContent="center"
						spacing={2}
						flexWrap={{
							xs: 'wrap',
							md: 'nowrap',
						}}
					>
						<Button variant="contained">Download / Convert</Button>
						<Button variant="contained">Reset</Button>
					</Stack>
				</Stack>
			</Box>
		</Container>
	);
};

export default MusicDownloader;
