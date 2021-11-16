import React, { useMemo } from 'react';
import { Container, Stack, Box, Divider } from '@mui/material';
import MusicContextProvider from '../context/Music';
import MusicForm from '../components/Music/MusicForm';
import JobList from '../components/Music/JobList';

const MusicDownloader = () => {
	const Page = useMemo(() => {
		return (
			<Stack direction={{ xs: 'column', md: 'row' }}>
				<Box sx={{ flex: 2 }}>
					<Container>
						<MusicForm />
					</Container>
				</Box>
				<Divider orientation="vertical" flexItem />
				<Box sx={{ flex: 1 }}>
					<Container>
						<JobList />
					</Container>
				</Box>
			</Stack>
		);
	}, []);

	return <MusicContextProvider>{Page}</MusicContextProvider>;
};

export default MusicDownloader;
