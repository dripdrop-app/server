import { Stack } from '@mui/material';
import MusicForm from '../components/Music/MusicForm';
import JobList from '../components/Music/JobList';

const MusicDownloader = () => {
	return (
		<Stack>
			<MusicForm />
			<JobList />
		</Stack>
	);
};

export default MusicDownloader;
