import { Stack } from '@mui/material';
import JobList from '../components/Music/JobList';
import MusicForm from '../components/Music/MusicForm';

const MusicDownloader = () => {
	return (
		<Stack direction="column">
			<MusicForm />
			<JobList />
		</Stack>
	);
};

export default MusicDownloader;
