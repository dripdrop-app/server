import React from 'react';
import { Container, Stack, Divider, Typography } from '@mui/material';
import MusicForm from '../components/Music/MusicForm';
import JobList from '../components/Music/JobList';

const MusicDownloader = () => {
	return (
		<Stack sx={{ m: 5 }}>
			<Typography sx={{ mb: 5 }} variant="h2">
				MP3 Downloader / Converter
			</Typography>
			<Stack direction="row">
				<Container sx={{ flex: 2 }}>
					<MusicForm />
				</Container>
				<Divider orientation="vertical" flexItem />
				<Container sx={{ flex: 1 }}>
					<JobList />
				</Container>
			</Stack>
		</Stack>
	);
};

export default MusicDownloader;
