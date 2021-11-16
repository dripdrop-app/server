import { useContext, useMemo, useCallback, useEffect } from 'react';
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
import { SxProps } from '@mui/system';
import { MusicContext } from '../../context/Music';
import { FILE_TYPE } from '../../utils/enums';
import Image from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';

interface JobCardProps {
	index: number;
}

const JobCard = (props: JobCardProps) => {
	const { removeJob, updateFormInputs, jobs } = useContext(MusicContext);
	const typographyDefaultCSS = useMemo(() => ({ textOverflow: 'ellipsis', whiteSpace: 'nowrap' }), []) as SxProps;
	const { index } = props;
	const job = useMemo(() => jobs[index], [index, jobs]);
	const { job_id, filename, youtube_url, title, artist, album, grouping, artwork_url, completed, failed } = job;

	const [downloadJob, downloadJobStatus] = useLazyFetch();

	const tryDownloadJob = useCallback(() => {
		const params = new URLSearchParams();
		params.append('job_id', job_id);
		downloadJob(`/music/downloadJob?${params}`);
	}, [downloadJob, job_id]);

	useEffect(() => {
		if (downloadJobStatus.isSuccess) {
			const response = downloadJobStatus.response;
			const data = downloadJobStatus.data;
			if (response) {
				const contentDisposition = response.headers.get('Content-Disposition') || '';
				const groups = contentDisposition.match(/filename\*?=(?:utf-8''|")(.+)(?:"|;)?/);
				const filename = decodeURIComponent(groups && groups.length > 1 ? groups[1] : 'downloaded.mp3');
				const url = URL.createObjectURL(data);
				const a = document.createElement('a');
				a.href = url;
				a.download = filename;
				a.click();
			}
		}
	}, [downloadJobStatus.data, downloadJobStatus.isSuccess, downloadJobStatus.response]);

	return useMemo(
		() => (
			<Card>
				<Container sx={{ my: 1 }}>
					<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center">
						<CardMedia component="img" height="150" image={artwork_url || Image} alt="artwork" />
						<CardContent sx={{ flex: 2 }}>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">ID:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{job_id}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Source:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{filename || youtube_url}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Title:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{title}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Artist:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{artist}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Album:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{album}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Grouping:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{grouping}
								</Typography>
							</Stack>
							<CardActions>
								{!completed && !failed ? <CircularProgress /> : null}
								<ButtonGroup variant="contained">
									{completed && !failed ? (
										<Button title="Download File" color="success" onClick={() => tryDownloadJob()}>
											<FileDownload />
										</Button>
									) : null}
									{failed ? (
										<Button title="Job Failed / File Not Found" color="error">
											<Error />
										</Button>
									) : null}
									<Button
										title="Copy to Form"
										onClick={() =>
											updateFormInputs({
												...job,
												fileType: FILE_TYPE.YOUTUBE,
												youtube_url: youtube_url || '',
												filename: '',
												artwork_url: artwork_url || '',
												grouping: grouping || '',
											})
										}
									>
										<CopyAll />
									</Button>
									<Button title="Delete Job and File" color="error" onClick={() => removeJob(job_id)}>
										<Delete />
									</Button>
								</ButtonGroup>
							</CardActions>
						</CardContent>
					</Stack>
				</Container>
			</Card>
		),
		[
			album,
			artist,
			artwork_url,
			completed,
			failed,
			filename,
			grouping,
			job,
			job_id,
			removeJob,
			title,
			tryDownloadJob,
			typographyDefaultCSS,
			updateFormInputs,
			youtube_url,
		]
	);
};

export default JobCard;
