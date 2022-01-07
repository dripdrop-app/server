import React, { useCallback, useEffect } from 'react';
import {
	Button,
	Card,
	CardContent,
	CardMedia,
	CircularProgress,
	Container,
	Link,
	Pagination,
	Stack,
	ToggleButton,
	ToggleButtonGroup,
	Typography,
} from '@mui/material';
import { useRecoilState } from 'recoil';
import { subscriptionsAtom } from '../../atoms/YoutubeCollections';
import useLazyFetch from '../../hooks/useLazyFetch';
import CustomGrid from './CustomGrid';
import _ from 'lodash';

const SubscriptionsView = () => {
	const [subscriptionsView, setSubscriptionsView] = useRecoilState(subscriptionsAtom);
	const [getSubscriptions, getSubscriptionsState] = useLazyFetch<YoutubeSubscriptionResponse>();

	const { subscriptions, per_page, page, total_subscriptions } = subscriptionsView;

	const querySubscriptions = useCallback(
		(params: Required<PageState>) => {
			setSubscriptionsView((prev) => ({ ...prev, ...params }));
			getSubscriptions({ url: `/youtube/subscriptions/${params.page}/${params.per_page}` });
		},
		[getSubscriptions, setSubscriptionsView]
	);

	const updateFilters = useCallback(
		(opt: Partial<PageState>) => {
			opt = {
				per_page: opt.per_page ?? per_page,
				page: opt.page ?? page,
			};
			if (!_.isEqual(opt, { per_page, page })) {
				querySubscriptions(opt as Required<PageState>);
			}
		},
		[page, per_page, querySubscriptions]
	);

	useEffect(() => {
		if (getSubscriptionsState.isSuccess) {
			const { subscriptions, total_subscriptions } = getSubscriptionsState.data;
			setSubscriptionsView((prev) => ({ ...prev, subscriptions, total_subscriptions, loaded: true }));
		}
	}, [getSubscriptionsState.data, getSubscriptionsState.isSuccess, setSubscriptionsView]);

	useEffect(() => {
		if (!subscriptionsView.loaded && !getSubscriptionsState.started) {
			querySubscriptions(subscriptionsView);
		}
	}, [getSubscriptionsState.started, querySubscriptions, subscriptionsView]);

	if (getSubscriptionsState.isLoading || !subscriptionsView.loaded) {
		return (
			<Stack justifyContent="center" direction="row" sx={{ my: 5 }}>
				<CircularProgress />
			</Stack>
		);
	}

	return (
		<React.Fragment>
			<Container sx={{ my: 5 }}>
				<Stack sx={{ my: 2 }} direction="row" justifyContent="flex-end">
					<ToggleButtonGroup exclusive value={per_page} onChange={(e, v) => updateFilters({ per_page: v })}>
						{([10, 25, 50] as PageState['per_page'][]).map((v) => (
							<ToggleButton key={v} value={v}>
								{v}
							</ToggleButton>
						))}
					</ToggleButtonGroup>
				</Stack>
				<CustomGrid
					items={subscriptions}
					renderItem={(subscription) => {
						const publishedAt = new Date(subscription.published_at).toLocaleDateString();
						return (
							<Card sx={{ height: '100%' }}>
								<Link sx={{ flex: 2 }} target="_blank" href={`https://youtube.com/channel/${subscription.channel_id}`}>
									<CardMedia component="img" image={subscription.channel_thumbnail} />
								</Link>
								<CardContent sx={{ flex: 1 }}>
									<Typography variant="subtitle1">
										<Link
											sx={{ textDecoration: 'none' }}
											target="_blank"
											href={`https://youtube.com/channel/${subscription.channel_id}`}
										>
											{subscription.channel_title}
										</Link>
									</Typography>
								</CardContent>
								<CardContent>
									<Stack>
										<Button variant="contained">show videos</Button>
									</Stack>
								</CardContent>
								<CardContent>
									<Stack direction="column">
										<Typography variant="caption">Subscribed: {publishedAt}</Typography>
									</Stack>
								</CardContent>
							</Card>
						);
					}}
				/>
				<Stack direction="row" sx={{ my: 5 }} justifyContent="center">
					<Pagination
						page={page}
						onChange={(e, page) => updateFilters({ page })}
						count={Math.ceil(total_subscriptions / per_page)}
						color="primary"
					/>
				</Stack>
			</Container>
		</React.Fragment>
	);
};

export default SubscriptionsView;
