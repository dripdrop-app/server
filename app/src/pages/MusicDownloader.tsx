import { Container, Grid } from 'semantic-ui-react';
import MusicForm from '../components/Music/MusicForm';
import JobList from '../components/Music/JobList';

const MusicDownloader = () => {
	return (
		<Container>
			<Grid stackable padded divided>
				<Grid.Row>
					<Grid.Column>
						<MusicForm />
					</Grid.Column>
				</Grid.Row>
				<Grid.Row>
					<Grid.Column>
						<JobList />
					</Grid.Column>
				</Grid.Row>
			</Grid>
		</Container>
	);
};

export default MusicDownloader;
