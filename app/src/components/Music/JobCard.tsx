import { Link } from 'react-router-dom';
import {
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
import { Download, Delete } from '@mui/icons-material';
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
				<Link to={props.downloadUrl} target="_blank" download>
					<LoadingButton variant="contained" color="success" startIcon={<Download />}>
						Download
					</LoadingButton>
				</Link>
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
