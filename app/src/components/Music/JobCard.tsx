import { useCallback, useEffect, useMemo } from 'react';
import { useAtomValue, useSetAtom, useAtom } from 'jotai';
import { FileDownload, CopyAll, Delete, Error } from '@mui/icons-material';
import {
	Card,
	Container,
	Stack,
	CardMedia,
	CardContent,
	Typography,
	CardActions,
	CircularProgress,
	ButtonGroup,
	Button,
} from '@mui/material';
import { jobAtom, jobsAtom, musicFormAtom } from '../../state/Music';
import { FILE_TYPE } from '../../utils/enums';
import Image from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';
import { typographyDefaultCSS } from '../../utils/helpers';

interface JobCardProps {
	id: string;
}

const JobCard = (props: JobCardProps) => {
	const { id } = props;
	const [jobs, setJobs] = useAtom(jobsAtom);
	const setMusicForm = useSetAtom(musicFormAtom);
	const job = useAtomValue(jobAtom(id));

	const [downloadJob, downloadJobStatus] = useLazyFetch<Blob>();
	const [removeJob, removeJobStatus] = useLazyFetch();

	const copyJob = useCallback(() => {
		if (job) {
			setMusicForm({
				...job,
				grouping: job.grouping || '',
				fileType: FILE_TYPE.YOUTUBE,
				youtubeUrl: job.youtubeUrl || '',
				filename: '',
				artworkUrl: job.artworkUrl || '',
			});
		}
	}, [job, setMusicForm]);

	useEffect(() => {
		if (removeJobStatus.success) {
			setJobs(jobs.filter((job) => job.id !== id));
		}
	}, [id, jobs, removeJobStatus.data, removeJobStatus.success, setJobs]);

	useEffect(() => {
		if (downloadJobStatus.success) {
			const response = downloadJobStatus.response;
			const data = downloadJobStatus.data;
			if (response) {
				const contentDisposition = response.headers['content-disposition'] || '';
				const groups = contentDisposition.match(/filename\*?=(?:utf-8''|")(.+)(?:"|;)?/);
				const filename = decodeURIComponent(groups && groups.length > 1 ? groups[1] : 'downloaded.mp3');
				const url = URL.createObjectURL(data);
				const a = document.createElement('a');
				a.href = url;
				a.download = filename;
				a.click();
			}
		}
	}, [downloadJobStatus.data, downloadJobStatus.response, downloadJobStatus.success]);

	return useMemo(
		() =>
			!job ? null : (
				<Card>
					<Container sx={{ my: 1 }}>
						<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center">
							<CardMedia component="img" height="150" image={job.artworkUrl || Image} alt="artwork" />
							<CardContent sx={{ flex: 2 }}>
								<Stack direction="row" spacing={1}>
									<Typography variant="caption">ID:</Typography>
									<Typography sx={typographyDefaultCSS} variant="caption">
										{id}
									</Typography>
								</Stack>
								<Stack direction="row" spacing={1}>
									<Typography variant="caption">Source:</Typography>
									<Typography sx={typographyDefaultCSS} variant="caption">
										{job.filename || job.youtubeUrl}
									</Typography>
								</Stack>
								<Stack direction="row" spacing={1}>
									<Typography variant="caption">Title:</Typography>
									<Typography sx={typographyDefaultCSS} variant="caption">
										{job.title}
									</Typography>
								</Stack>
								<Stack direction="row" spacing={1}>
									<Typography variant="caption">Artist:</Typography>
									<Typography sx={typographyDefaultCSS} variant="caption">
										{job.artist}
									</Typography>
								</Stack>
								<Stack direction="row" spacing={1}>
									<Typography variant="caption">Album:</Typography>
									<Typography sx={typographyDefaultCSS} variant="caption">
										{job.album}
									</Typography>
								</Stack>
								<Stack direction="row" spacing={1}>
									<Typography variant="caption">Grouping:</Typography>
									<Typography sx={typographyDefaultCSS} variant="caption">
										{job.grouping}
									</Typography>
								</Stack>
								<CardActions>
									{!job.completed && !job.failed ? <CircularProgress /> : null}
									<ButtonGroup variant="contained">
										{job.completed && !job.failed ? (
											<Button
												title="Download File"
												color="success"
												onClick={() => downloadJob({ url: `/music/jobs/download/${id}`, responseType: 'blob' })}
											>
												<FileDownload />
											</Button>
										) : null}
										{job.failed ? (
											<Button title="Job Failed / File Not Found" color="error">
												<Error />
											</Button>
										) : null}
										<Button title="Copy to Form" onClick={() => copyJob()}>
											<CopyAll />
										</Button>
										<Button
											title="Delete Job and File"
											color="error"
											onClick={() => removeJob({ url: `/music/jobs/delete/${id}`, method: 'DELETE' })}
										>
											<Delete />
										</Button>
									</ButtonGroup>
								</CardActions>
							</CardContent>
						</Stack>
					</Container>
				</Card>
			),
		[copyJob, downloadJob, id, job, removeJob]
	);
};

export default JobCard;
