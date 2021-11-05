import React, { useCallback, useContext, useMemo, useState } from 'react';
import {
	Card,
	CardContent,
	CardMedia,
	CardActions,
	Typography,
	CircularProgress,
	Button,
	Stack,
	Box,
	Container,
	ButtonGroup,
} from '@mui/material';
import { FileDownload, CopyAll, Delete, Error, NavigateNext, NavigateBefore } from '@mui/icons-material';
import { Job, MusicContext } from '../../context/music_context';
import Image from '../../images/blank_image.jpeg';
import { SxProps } from '@mui/system';
import { FILE_TYPE } from '../../utils/enums';

const JobCard = (props: Job) => {
	const { removeJob, updateFormInputs } = useContext(MusicContext);
	const typographyDefaultCSS = useMemo(() => ({ textOverflow: 'ellipsis', whiteSpace: 'nowrap' }), []) as SxProps;
	const { jobID, filename, youtubeURL, artworkURL, title, artist, album, grouping, completed, failed } = props;

	const downloadJob = useCallback(async () => {
		const params = new URLSearchParams();
		params.append('jobID', jobID);
		const response = await fetch(`/music/downloadJob?${params}`);
		if (response.ok) {
			const contentDisposition = response.headers.get('Content-Disposition') || '';
			const groups = contentDisposition.match(/filename\*?=(?:utf-8''|")(.+)(?:"|;)?/);
			const filename = decodeURIComponent(groups && groups.length > 1 ? groups[1] : 'downloaded.mp3');
			const url = URL.createObjectURL(await response.blob());
			const a = document.createElement('a');
			a.href = url;
			a.download = filename;
			a.click();
		}
	}, [jobID]);

	return useMemo(
		() => (
			<Card>
				<Container sx={{ my: 1 }}>
					<Stack direction={{ xs: 'column', md: 'row' }} alignItems="center">
						<CardMedia component="img" height="150" image={artworkURL || Image} alt="artwork" />
						<CardContent sx={{ flex: 2 }}>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">ID:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{jobID}
								</Typography>
							</Stack>
							<Stack direction="row" spacing={1}>
								<Typography variant="caption">Source:</Typography>
								<Typography sx={typographyDefaultCSS} variant="caption">
									{filename || youtubeURL}
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
										<Button title="Download File" color="success" onClick={downloadJob}>
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
										onClick={() => updateFormInputs({ ...props, fileType: FILE_TYPE.YOUTUBE })}
									>
										<CopyAll />
									</Button>
									<Button title="Delete Job and File" color="error" onClick={() => removeJob(jobID)}>
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
			artworkURL,
			completed,
			downloadJob,
			failed,
			filename,
			grouping,
			jobID,
			props,
			removeJob,
			title,
			typographyDefaultCSS,
			updateFormInputs,
			youtubeURL,
		]
	);
};

const JobList = () => {
	const [page, setPage] = useState(0);
	const { jobs } = useContext(MusicContext);
	const PAGE_SIZE = useMemo(() => 5, []);

	const prevPage = Math.max(page - 1, 0);
	const nextPage = Math.min(page + 1, jobs.length / PAGE_SIZE) - Number(jobs.length % PAGE_SIZE === 0);

	return useMemo(
		() => (
			<Stack sx={{ my: 5 }}>
				<Stack direction="row" justifyContent="center">
					<Button disabled={page - 1 < 0} onClick={() => setPage(prevPage)}>
						<NavigateBefore />
					</Button>
					<Typography variant="h5">Jobs</Typography>
					<Button disabled={page + 1 > jobs.length / PAGE_SIZE} onClick={() => setPage(nextPage)}>
						<NavigateNext />
					</Button>
				</Stack>
				<Stack textAlign="center" sx={{ my: 5 }}>
					{jobs.length === 0 ? <Typography variant="body2">No Existing Jobs</Typography> : null}
				</Stack>
				<Stack spacing={1} alignSelf="center" justifyContent="center">
					{jobs.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE).map((job) => (
						<Box key={job.jobID}>
							<JobCard {...job} />
						</Box>
					))}
				</Stack>
			</Stack>
		),
		[PAGE_SIZE, jobs, nextPage, page, prevPage]
	);
};

export default JobList;
