import React, { useContext, useMemo, useState } from 'react';
import {
	Card,
	CardContent,
	CardMedia,
	CardActions,
	Typography,
	CircularProgress,
	Button,
	Stack,
	List,
	ListItem,
} from '@mui/material';
import { FileDownload, CopyAll, Delete, Error } from '@mui/icons-material';
import { Job, MusicContext } from '../../context/music_context';
import Image from '../../images/blank_image.jpeg';
import { SxProps } from '@mui/system';
import { FILE_TYPE } from '../../utils/enums';

const JobCard = (props: Job) => {
	const { removeJob, updateFormInputs } = useContext(MusicContext);
	const typographyDefaultCSS = useMemo(() => ({ textOverflow: 'ellipsis', whiteSpace: 'nowrap' }), []) as SxProps;
	const { jobID, filename, youtubeURL, artworkURL, title, artist, album, grouping, completed, failed } = props;

	return useMemo(
		() => (
			<Card>
				<CardMedia component="img" image={artworkURL || Image} alt="artwork" />
				<CardContent>
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
				</CardContent>
				<CardActions>
					{completed ? (
						<Button color="success">
							<FileDownload color="success" />
						</Button>
					) : null}
					{failed ? <Error color="error" /> : null}
					{!completed && !failed ? <CircularProgress /> : null}
					<Button onClick={() => updateFormInputs({ ...props, fileType: FILE_TYPE.YOUTUBE })}>
						<CopyAll />
					</Button>
					<Button color="error" onClick={() => removeJob(jobID)}>
						<Delete color="error" />
					</Button>
				</CardActions>
			</Card>
		),
		[
			album,
			artist,
			artworkURL,
			completed,
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

	return useMemo(
		() => (
			<Stack sx={{ my: 5 }}>
				<Stack direction="row">
					<Button onClick={() => setPage(Math.max(page - 1, 0))}>Prev</Button>
					<Typography variant="h5">Jobs</Typography>
					<Button
						onClick={() =>
							setPage(Math.min(page + 1, Math.floor(jobs.length / PAGE_SIZE) - Number(jobs.length % PAGE_SIZE === 0)))
						}
					>
						Next
					</Button>
				</Stack>
				<List sx={{ flexDirection: 'row' }}>
					{jobs.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE).map((job) => (
						<ListItem key={job.jobID}>
							<JobCard {...job} />
						</ListItem>
					))}
				</List>
			</Stack>
		),
		[PAGE_SIZE, jobs, page]
	);
};

export default JobList;
