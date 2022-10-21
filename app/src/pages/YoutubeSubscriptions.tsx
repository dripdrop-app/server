import { useMemo, useRef, useState } from 'react';
import { Container, Grid, Skeleton, Stack, Typography } from '@mui/material';
import InfiniteScroll from '../components/InfiniteScroll';
import YoutubePage from '../components/Youtube/Auth/YoutubePage';
import YoutubeSubscriptionsPage from '../components/Youtube/YoutubeSubscriptionsPage';
import YoutubeSubscriptionCard from '../components/Youtube/YoutubeSubscriptionCard';

const YoutubeSubscriptions = () => {
	const [pages, setPages] = useState(1);
	const pagesLoaded = useRef<Record<number, boolean>>({});

	const SubscriptionsView = useMemo(
		() => (
			<Stack spacing={2} paddingY={2}>
				{/* <InfiniteScroll
					items={Array(pages).fill(1)}
					renderItem={(page, index) => (
						<Grid container>
							<YoutubeSubscriptionsPage
								page={index + 1}
								perPage={48}
								onLoading={(page) => {
									pagesLoaded.current[page] = false;
								}}
								onLoaded={(page, subscriptions) => {
									if (subscriptions.length === 48) {
										pagesLoaded.current[page] = true;
									}
								}}
								renderLoadingItem={() => (
									<Grid item xs={12} sm={6} md={3} padding={1}>
										<Skeleton
											sx={(theme) => ({
												height: '40vh',
												[theme.breakpoints.only('xs')]: { width: '80vw' },
												[theme.breakpoints.only('sm')]: { width: '40vw' },
												[theme.breakpoints.up('md')]: { width: '20vw' },
												[theme.breakpoints.only('xl')]: { width: '10vw' },
											})}
											variant="rectangular"
										/>
									</Grid>
								)}
								renderItem={(subscription) => (
									<Grid item xs={12} sm={6} md={3} padding={1}>
										<YoutubeSubscriptionCard sx={{ height: '100%' }} subscription={subscription} />
									</Grid>
								)}
							/>
						</Grid>
					)}
					onEndReached={() => {
						if (pagesLoaded.current[pages]) {
							setPages((page) => page + 1);
						}
					}}
				/> */}
			</Stack>
		),
		[pages]
	);

	return useMemo(
		() => (
			<Container>
				<Stack>
					<Typography variant="h3">Youtube Subscriptions</Typography>
					<YoutubePage>
						<Stack paddingY={2}>{SubscriptionsView}</Stack>
					</YoutubePage>
				</Stack>
			</Container>
		),
		[SubscriptionsView]
	);
};

export default YoutubeSubscriptions;
