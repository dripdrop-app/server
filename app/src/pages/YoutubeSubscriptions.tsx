import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { CircularProgress, Divider, Grid, Stack, Typography } from '@mui/material';
import { throttle } from 'lodash';
import { useYoutubeSubscriptionsQuery } from '../api/youtube';
import InfiniteScroll from '../components/InfiniteScroll';
import SubscriptionsPage from '../components/Youtube/SubscriptionsPage';
import SubscriptionCard from '../components/Youtube/SubscriptionCard';
import YoutubeAuthPage from '../components/Auth/YoutubeAuthPage';

const YoutubeSubscriptions = () => {
	const [filter, setFilter] = useState<YoutubeSubscriptionBody>({
		page: 1,
		perPage: 48,
	});
	const continueLoadingRef = useRef(false);

	const subscriptionsStatus = useYoutubeSubscriptionsQuery(filter);

	// eslint-disable-next-line react-hooks/exhaustive-deps
	const onEndReached = useCallback(
		throttle(() => {
			if (continueLoadingRef.current) {
				setFilter((prevState) => ({ ...prevState, page: prevState.page + 1 }));
			}
		}, 5000),
		[]
	);

	useEffect(() => {
		if (subscriptionsStatus.isSuccess && subscriptionsStatus.currentData) {
			const { subscriptions } = subscriptionsStatus.currentData;
			continueLoadingRef.current = subscriptions.length === filter.perPage;
		}
	}, [filter.perPage, subscriptionsStatus.currentData, subscriptionsStatus.isSuccess]);

	useEffect(() => {
		if (subscriptionsStatus.isFetching || subscriptionsStatus.isLoading) {
			continueLoadingRef.current = false;
		}
	}, [subscriptionsStatus.isFetching, subscriptionsStatus.isLoading]);

	return useMemo(
		() => (
			<YoutubeAuthPage>
				<Stack direction="column" spacing={2}>
					<Typography variant="h4">Subscriptions</Typography>
					<Divider />
					<InfiniteScroll
						items={Array(filter.page).fill(1)}
						renderItem={(page, index) => (
							<Grid container>
								<SubscriptionsPage
									perPage={filter.perPage}
									page={index + 1}
									renderItem={(subscription) => (
										<Grid item xs={12} sm={6} md={3} xl={2} padding={1}>
											<SubscriptionCard subscription={subscription} />
										</Grid>
									)}
									renderLoading={() => (
										<Grid item xs={12} padding={2}>
											<Stack direction="row" justifyContent="center">
												<CircularProgress />
											</Stack>
										</Grid>
									)}
								/>
							</Grid>
						)}
						onEndReached={onEndReached}
					/>
				</Stack>
			</YoutubeAuthPage>
		),
		[filter.page, filter.perPage, onEndReached]
	);
};

export default YoutubeSubscriptions;
