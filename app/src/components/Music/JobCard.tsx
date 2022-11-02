import { Link } from 'react-router-dom';
import {
	Button,
	Card,
	CardMedia,
	CardContent,
	TableContainer,
	Box,
	Table,
	TableBody,
	TableCell,
	Stack,
	TableRow,
} from '@mui/material';
import { Download, Delete, Error } from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';
import { useRemoveJobMutation } from '../../api/music';

const JobCard = (props: Job) => {
	const createdAt = new Date(props.createdAt).toLocaleDateString();

	const [removeJob, removeJobStatus] = useRemoveJobMutation();

	return (
		<Card>
			<CardMedia
				component="img"
				image={props.artworkUrl || 'https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/blank_image.jpeg'}
				alt={props.id}
			/>
			<CardContent>
				<TableContainer component={Box}>
					<Table>
						<TableBody>
							<TableRow>
								<TableCell>ID</TableCell>
								<TableCell>{props.id}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>Youtube URL</TableCell>
								<TableCell>{props.youtubeUrl}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>Filename</TableCell>
								<TableCell>{props.filename}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>Artwork URL</TableCell>
								<TableCell>{props.artworkUrl}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>Title</TableCell>
								<TableCell>{props.title}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>Artist</TableCell>
								<TableCell>{props.artist}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>Album</TableCell>
								<TableCell>{props.album}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>Grouping</TableCell>
								<TableCell>{props.grouping}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>Created</TableCell>
								<TableCell>{createdAt}</TableCell>
							</TableRow>
						</TableBody>
					</Table>
				</TableContainer>
			</CardContent>
			<Stack direction="row" justifyContent="center" paddingY={2} spacing={2} flexWrap="wrap">
				<Box display={props.completed || props.failed ? 'none' : 'contents'}>
					<LoadingButton variant="contained" color="primary" loading={true}>
						Loading
					</LoadingButton>
				</Box>
				<Box display={props.completed ? 'contents' : 'none'}>
					<Link to={props.downloadUrl || ''} target="_blank" download>
						<Button variant="contained" color="success" startIcon={<Download />}>
							Download
						</Button>
					</Link>
				</Box>
				<Box display={props.failed ? 'contents' : 'none'}>
					<Button variant="contained" color="error" startIcon={<Error />}>
						Failed
					</Button>
				</Box>
				<LoadingButton
					variant="contained"
					color="error"
					startIcon={<Delete />}
					loading={removeJobStatus.isLoading}
					onClick={() => removeJob(props.id)}
				>
					Delete
				</LoadingButton>
			</Stack>
		</Card>
	);
};

export default JobCard;
