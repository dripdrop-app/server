import { useContext, useMemo, useState } from 'react';
import { Typography, Button, Stack, Box } from '@mui/material';
import { NavigateNext, NavigateBefore } from '@mui/icons-material';
import { MusicContext } from '../../context/Music';
import JobCard from './JobCard';

const JobList = () => {
	const [page, setPage] = useState(0);
	const { jobs } = useContext(MusicContext);
	const jobs_length = useMemo(() => jobs.length, [jobs]);
	const PAGE_SIZE = useMemo(() => 5, []);

	const prevPage = Math.max(page - 1, 0);
	const nextPage = Math.min(page + 1, jobs_length / PAGE_SIZE) - Number(jobs_length % PAGE_SIZE === 0);

	const indices = useMemo(() => {
		const arr = [];
		for (let i = 0; i < PAGE_SIZE; i++) {
			arr.push(page * PAGE_SIZE + i);
		}
		return arr;
	}, [PAGE_SIZE, page]);

	return useMemo(
		() => (
			<Stack sx={{ my: 5 }}>
				<Stack direction="row" justifyContent="center">
					<Button disabled={page - 1 < 0} onClick={() => setPage(prevPage)}>
						<NavigateBefore />
					</Button>
					<Typography variant="h5">Jobs</Typography>
					<Button disabled={page + 1 > jobs_length / PAGE_SIZE} onClick={() => setPage(nextPage)}>
						<NavigateNext />
					</Button>
				</Stack>
				<Stack textAlign="center" sx={{ my: 5 }}>
					{jobs_length === 0 ? <Typography variant="body2">No Existing Jobs</Typography> : null}
				</Stack>
				<Stack spacing={1} alignSelf="center" justifyContent="center">
					{indices.map((job_index) =>
						jobs[job_index] ? (
							<Box key={job_index}>
								<JobCard index={job_index} />
							</Box>
						) : null
					)}
				</Stack>
			</Stack>
		),
		[PAGE_SIZE, indices, jobs, jobs_length, nextPage, page, prevPage]
	);
};

export default JobList;
