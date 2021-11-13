import React from 'react';
import { Container, Stack, Box, Divider } from '@mui/material';
import MusicContextProvider, { MusicContext, MusicContextValue } from '../context/Music';
import MusicForm from '../components/Music/MusicForm';
import JobList from '../components/Music/JobList';
import { ConsumerComponent } from '../components/ConsumerComponent';

const MusicDownloader = () => {
	return (
		<MusicContextProvider>
			<Stack direction={{ xs: 'column', md: 'row' }}>
				<Box sx={{ flex: 2 }}>
					<Container>
						<MusicForm />
					</Container>
				</Box>
				<Divider orientation="vertical" flexItem />
				<Box sx={{ flex: 1 }}>
					<ConsumerComponent
						context={MusicContext}
						selector={(context: MusicContextValue) => ({
							jobs: context.jobs,
						})}
						render={(props) => (
							<Container>
								<JobList {...props} />
							</Container>
						)}
					/>
				</Box>
			</Stack>
		</MusicContextProvider>
	);
};

export default MusicDownloader;
