import React, { useCallback, useEffect, useState } from 'react';
import {
	Button,
	Card,
	CardContent,
	CardMedia,
	CircularProgress,
	Container,
	Dialog,
	DialogContent,
	DialogTitle,
	IconButton,
	Link,
	Pagination,
	Stack,
	ToggleButton,
	ToggleButtonGroup,
	Typography,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import { useRecoilState } from 'recoil';
import { subscriptionsAtom } from '../../atoms/YoutubeCollections';
import useLazyFetch from '../../hooks/useLazyFetch';
import CustomGrid from './CustomGrid';
import _ from 'lodash';
import VideosView from './VideosView';
import { Variant } from '@mui/material/styles/createTypography';

const SubscriptionsView = () => {
	const [subscriptionsView, setSubscriptionsView] = useRecoilState(subscriptionsAtom);
	const [getSubscriptions, getSubscriptionsState] = useLazyFetch<YoutubeSubscriptionResponse>();
	const [showModal, setShowModal] = useState(false);
	const [selectedSubscription, setSelectedSubscription] = useState<null | YoutubeSubscription>(null);

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

	const showChannelVideos = useCallback((subscription: YoutubeSubscription) => {
		setSelectedSubscription(subscription);
		setShowModal(true);
	}, []);

	const ChannelLink = (variant: Variant, subscription: YoutubeSubscription) => {
		return (
			<Typography variant={variant}>
				<Link
					sx={{ textDecoration: 'none' }}
					target="_blank"
					href={`https://youtube.com/channel/${subscription.channel_id}`}
				>
					{subscription.channel_title}
				</Link>
			</Typography>
		);
	};

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
			<Dialog maxWidth="lg" fullWidth open={showModal} onClose={() => setShowModal(false)}>
				{selectedSubscription ? (
					<React.Fragment>
						<DialogTitle>
							<Stack direction="row" justifyContent="space-between">
								{ChannelLink('h3', selectedSubscription)}
								<IconButton onClick={() => setShowModal(false)}>
									<Close />
								</IconButton>
							</Stack>
						</DialogTitle>
						<DialogContent dividers>
							<VideosView channelID={selectedSubscription.channel_id} />
						</DialogContent>
					</React.Fragment>
				) : null}
			</Dialog>
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
								<CardContent sx={{ flex: 1 }}>{ChannelLink('subtitle1', subscription)}</CardContent>
								<CardContent>
									<Stack>
										<Button variant="contained" onClick={() => showChannelVideos(subscription)}>
											show videos
										</Button>
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