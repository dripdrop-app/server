import { Container, Stack } from '@mui/material';
import MusicForm from '../components/Music/MusicForm';
import JobList from '../components/Music/JobList';

const MusicDownloader = () => {
	return (
		<Container>
			<Stack>
				<MusicForm />
				<JobList />
			</Stack>
		</Container>
	);
};

export default MusicDownloader;
