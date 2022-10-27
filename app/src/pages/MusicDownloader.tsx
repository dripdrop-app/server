import { Stack } from '@mui/material';
import AuthPage from '../components/Auth/AuthPage';
import JobList from '../components/Music/JobList';
import MusicForm from '../components/Music/MusicForm';

const MusicDownloader = () => {
	return (
		<AuthPage>
			<Stack spacing={2} direction="column">
				<MusicForm />
				<JobList />
			</Stack>
		</AuthPage>
	);
};

export default MusicDownloader;
