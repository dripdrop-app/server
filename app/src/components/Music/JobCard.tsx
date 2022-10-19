import { Link } from 'react-router-dom';
import { Card, CardMedia, CardContent, TableContainer, Box, Table, TableBody, TableCell, Stack } from '@mui/material';
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
							<TableCell>ID</TableCell>
							<TableCell>{props.id}</TableCell>
						</TableBody>
						<TableBody>
							<TableCell>Youtube URL</TableCell>
							<TableCell>{props.youtubeUrl}</TableCell>
						</TableBody>
						<TableBody>
							<TableCell>Filename</TableCell>
							<TableCell>{props.filename}</TableCell>
						</TableBody>
						<TableBody>
							<TableCell>Artwork URL</TableCell>
							<TableCell>{props.artworkUrl}</TableCell>
						</TableBody>
						<TableBody>
							<TableCell>Title</TableCell>
							<TableCell>{props.title}</TableCell>
						</TableBody>
						<TableBody>
							<TableCell>Artist</TableCell>
							<TableCell>{props.artist}</TableCell>
						</TableBody>
						<TableBody>
							<TableCell>Album</TableCell>
							<TableCell>{props.album}</TableCell>
						</TableBody>
						<TableBody>
							<TableCell>Grouping</TableCell>
							<TableCell>{props.grouping}</TableCell>
						</TableBody>
						<TableBody>
							<TableCell>Created</TableCell>
							<TableCell>{createdAt}</TableCell>
						</TableBody>
					</Table>
				</TableContainer>
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
			</CardContent>
		</Card>
	);
};

export default JobCard;
