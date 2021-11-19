import { useMemo, useCallback, useEffect } from 'react';
import { useRecoilValue, useSetRecoilState } from 'recoil';
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
import {
	albumSelector,
	artistSelector,
	artworkURLSelector,
	filenameSelector,
	fileTypeSelector,
	groupingSelector,
	jobAtom,
	jobsAtom,
	titleSelector,
	youtubeURLSelector,
} from '../../atoms/Music';
import { FILE_TYPE } from '../../utils/enums';
import Image from '../../images/blank_image.jpeg';
import useLazyFetch from '../../hooks/useLazyFetch';
import { typographyDefaultCSS } from '../../utils/helpers';

interface JobCardProps {
	id: string;
}

const JobCard = (props: JobCardProps) => {
	const setJobs = useSetRecoilState(jobsAtom);
	const setTitle = useSetRecoilState(titleSelector);
	const setArtist = useSetRecoilState(artistSelector);
	const setAlbum = useSetRecoilState(albumSelector);
	const setGrouping = useSetRecoilState(groupingSelector);
	const setArtworkURL = useSetRecoilState(artworkURLSelector);
	const setYoutubeURL = useSetRecoilState(youtubeURLSelector);
	const setFileType = useSetRecoilState(fileTypeSelector);
	const setFilename = useSetRecoilState(filenameSelector);

	const { id } = props;
	const job = useRecoilValue(jobAtom(id));

	const { job_id, filename, youtube_url, title, artist, album, grouping, artwork_url, completed, failed } = job;

	const [downloadJob, downloadJobStatus] = useLazyFetch();
	const [removeJob, removeJobStatus] = useLazyFetch();

	const tryDownloadJob = useCallback(() => {
		const params = new URLSearchParams();
		params.append('job_id', job_id || '');
		downloadJob(`/music/downloadJob?${params}`);
	}, [downloadJob, job_id]);

	const tryRemoveJob = useCallback(
		async (deletedJobID: string) => {
			const params = new URLSearchParams();
			params.append('job_id', deletedJobID);
			removeJob(`/music/deleteJob?${params}`);
		},
		[removeJob]
	);

	const copyJob = useCallback(() => {
		setTitle(title);
		setArtist(artist);
		setAlbum(album);
		setGrouping(grouping || '');
		setFileType(FILE_TYPE.YOUTUBE);
		setYoutubeURL(youtube_url || '');
		setFilename('');
		setArtworkURL(artwork_url || '');
	}, [
		album,
		artist,
		artwork_url,
		grouping,
		setAlbum,
		setArtist,
		setArtworkURL,
		setFileType,
		setFilename,
		setGrouping,
		setTitle,
		setYoutubeURL,
		title,
		youtube_url,
	]);

	useEffect(() => {
		if (removeJobStatus.isSuccess) {
			setJobs((jobs) => jobs.filter((job) => job.job_id !== job_id));
		}
	}, [job_id, removeJobStatus.isSuccess, setJobs]);

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
									<Button title="Copy to Form" onClick={() => copyJob()}>
										<CopyAll />
									</Button>
									<Button title="Delete Job and File" color="error" onClick={() => tryRemoveJob(job_id)}>
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
			copyJob,
			failed,
			filename,
			grouping,
			job_id,
			title,
			tryDownloadJob,
			tryRemoveJob,
			youtube_url,
		]
	);
};

export default JobCard;
