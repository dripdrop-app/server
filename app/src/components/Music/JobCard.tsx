import { useCallback, useEffect, useMemo } from 'react';
import {
	Card,
	Button,
	ButtonGroup,
	CardContent,
	Stack,
	CardMedia,
	SxProps,
	Theme,
	List,
	ListItem,
	ListItemText,
	CardActions,
	Box,
	CircularProgress,
} from '@mui/material';
import { Error } from '@mui/icons-material';
import { useDispatch } from 'react-redux';
import { useRemoveJobMutation, useLazyDownloadJobQuery } from '../../api/music';
import { FILE_TYPE } from '../../utils/enums';
import { updateForm } from '../../state/music';
import { CopyAll, Delete, Download } from '@mui/icons-material';
import ConditionalDisplay from '../ConditionalDisplay';

interface JobCardProps {
	job: Job;
	sx?: SxProps<Theme>;
}

const JobCard = (props: JobCardProps) => {
	const { job, sx } = props;

	const [removeJob] = useRemoveJobMutation();
	const [downloadJob, downloadJobStatus] = useLazyDownloadJobQuery();

	const dispatch = useDispatch();

	const copyJob = useCallback(() => {
		dispatch(
			updateForm({
				...job,
				grouping: job.grouping || '',
				fileType: FILE_TYPE.YOUTUBE,
				youtubeUrl: job.youtubeUrl || '',
				filename: '',
				artworkUrl: job.artworkUrl || '',
			})
		);
	}, [dispatch, job]);

	useEffect(() => {
		if (downloadJobStatus.isSuccess && downloadJobStatus.currentData) {
			const url = downloadJobStatus.currentData.url;
			const a = document.createElement('a');
			a.href = url;
			a.click();
		}
	}, [downloadJobStatus.currentData, downloadJobStatus.isSuccess]);

	return useMemo(
		() => (
			<Card sx={sx}>
				<Stack height="100%" alignItems="center">
					<CardMedia
						component="img"
						image={job.artworkUrl || 'https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/blank_image.jpeg'}
					/>
					<CardContent>
						<List>
							<ListItem>
								<Stack>
									<ListItemText secondary="ID" />
									<ListItemText primary={job.id} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Source" />
									<ListItemText primary={job.filename || job.youtubeUrl} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Title" />
									<ListItemText primary={job.title} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Artist" />
									<ListItemText primary={job.artist} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Album" />
									<ListItemText primary={job.album} />
								</Stack>
							</ListItem>
							<ListItem>
								<Stack>
									<ListItemText secondary="Grouping" />
									<ListItemText primary={job.grouping || 'None'} />
								</Stack>
							</ListItem>
						</List>
					</CardContent>
					<Box flex={1} />
					<CardActions>
						<Stack direction="row" justifyContent="center">
							<ButtonGroup>
								<ConditionalDisplay condition={!job.completed && !job.failed}>
									<Button>
										<CircularProgress />
									</Button>
								</ConditionalDisplay>
								<ConditionalDisplay condition={job.failed}>
									<Button color="error" disabled>
										<Error />
									</Button>
								</ConditionalDisplay>
								<ConditionalDisplay condition={job.completed}>
									<Button color="success" onClick={() => downloadJob(job.id)}>
										<Download />
									</Button>
								</ConditionalDisplay>
								<Button onClick={() => copyJob()}>
									<CopyAll />
								</Button>
								<Button color="error" onClick={() => removeJob(job.id)}>
									<Delete />
								</Button>
							</ButtonGroup>
						</Stack>
					</CardActions>
				</Stack>
			</Card>
		),
		[
			copyJob,
			downloadJob,
			job.album,
			job.artist,
			job.artworkUrl,
			job.completed,
			job.failed,
			job.filename,
			job.grouping,
			job.id,
			job.title,
			job.youtubeUrl,
			removeJob,
			sx,
		]
	);
};

export default JobCard;
