import { useCallback, useMemo } from 'react';
import { Button, Card, Container, Grid, Image, List } from 'semantic-ui-react';
import { useDispatch } from 'react-redux';
import { useRemoveJobMutation, useLazyDownloadJobQuery } from '../../api';
import { FILE_TYPE } from '../../utils/enums';
import BlankImage from '../../images/blank_image.jpeg';
import { updateForm } from '../../state/music';

interface JobCardProps {
	job: Job;
}

const JobCard = (props: JobCardProps) => {
	const { job } = props;

	const [removeJob] = useRemoveJobMutation();
	const [downloadJob] = useLazyDownloadJobQuery();

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

	const download = useCallback(async () => {
		const result = await downloadJob(job.id);
		if (result.isSuccess) {
			const response = result.data;
			const data = await response.blob();
			const contentDisposition = response.headers.get('content-disposition') || '';
			const groups = contentDisposition.match(/filename\*?=(?:utf-8''|")(.+)(?:"|;)?/);
			const filename = decodeURIComponent(groups && groups.length > 1 ? groups[1] : 'downloaded.mp3');
			const url = URL.createObjectURL(data);
			const a = document.createElement('a');
			a.href = url;
			a.download = filename;
			a.click();
		}
	}, [downloadJob, job.id]);

	return useMemo(() => {
		if (!job) {
			return null;
		}
		return (
			<Card fluid>
				<Image fluid src={job.artworkUrl || BlankImage} />
				<Card.Content>
					<Card.Description textAlign="left">
						<List>
							<List.Item>
								<List.Header>ID</List.Header>
								{job.id}
							</List.Item>
							<List.Item>
								<List.Header>Source</List.Header>
								{job.filename || job.youtubeUrl}
							</List.Item>
						</List>
					</Card.Description>
				</Card.Content>
				<Card.Content>
					<Card.Description textAlign="center">
						<List horizontal>
							<List.Item>
								<List.Header>Title</List.Header>
								{job.title}
							</List.Item>
							<List.Item>
								<List.Header>Artist</List.Header>
								{job.artist}
							</List.Item>
							<List.Item>
								<List.Header>Album</List.Header>
								{job.album}
							</List.Item>
							<List.Item>
								<List.Header>Grouping</List.Header>
								{job.grouping}
							</List.Item>
						</List>
					</Card.Description>
				</Card.Content>
				<Card.Content extra>
					<Container>
						<Grid container stackable>
							<Grid.Row columns="equal">
								<Grid.Column>
									{!job.failed ? (
										<Button
											fluid
											loading={!job.completed}
											icon="cloud download"
											color="green"
											onClick={() => download()}
										/>
									) : null}
									{job.failed ? <Button fluid icon="x" color="red" /> : null}
								</Grid.Column>
								<Grid.Column>
									<Button icon="copy" fluid onClick={() => copyJob()} />
								</Grid.Column>
								<Grid.Column>
									<Button icon="trash" color="red" fluid onClick={() => removeJob(job.id)} />
								</Grid.Column>
							</Grid.Row>
						</Grid>
					</Container>
				</Card.Content>
			</Card>
		);
	}, [copyJob, download, job, removeJob]);
};

export default JobCard;
