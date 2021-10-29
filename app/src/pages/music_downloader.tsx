import React from 'react';
import { Container, Stack, Box } from '@mui/material';
import MusicForm from '../components/Music/music_form';
import JobList from '../components/Music/job_list';

const MusicDownloader = () => {
	return (
		<Stack direction="row">
			<Box sx={{ flex: 5 }}>
				<Container>
					<MusicForm />
				</Container>
			</Box>
			<Box sx={{ flex: 1 }}>
				<Container>
					<JobList />
				</Container>
			</Box>
		</Stack>
	);
};

export default MusicDownloader;
