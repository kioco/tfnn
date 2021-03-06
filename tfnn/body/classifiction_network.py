from tfnn.body.network import Network
import tfnn


class ClfNetwork(Network):
    def __init__(self, n_inputs, n_outputs, method='softmax', do_dropout=False, do_l2=False, seed=None):
        if method == 'softmax':
            input_dtype = tfnn.float32
            output_dtype = tfnn.float32
            output_activator = tfnn.nn.softmax
        elif method == 'sigmoid':
            input_dtype = tfnn.float32
            output_dtype = tfnn.float32
            output_activator = tfnn.sigmoid
        else:
            raise ValueError("method should be one of ['softmax', 'sigmoid']")
        super(ClfNetwork, self).__init__(
            n_inputs, n_outputs, input_dtype, output_dtype, output_activator,
            do_dropout, do_l2, seed)
        self.method = method
        self.name = 'ClassificationNetwork'

    def _init_loss(self):
        with tfnn.name_scope('predictions'):
            if self.method == 'softmax':
                self.predictions = tfnn.nn.softmax(self.layers_final_output.iloc[-1], name='predictions')
            elif self.method == 'sigmoid':
                self.predictions = tfnn.nn.sigmoid(self.layers_final_output.iloc[-1], name='predictions')
        with tfnn.name_scope('loss'):
            if self.method == 'softmax':
                self.cross_entropy = tfnn.nn.softmax_cross_entropy_with_logits(
                    self.layers_final_output.iloc[-1],
                    self.target_placeholder,
                    name='xentropy')
            elif self.method == 'sigmoid':
                self.cross_entropy = tfnn.nn.sigmoid_cross_entropy_with_logits(
                    self.layers_final_output.iloc[-1],
                    self.target_placeholder,
                    name='xentropy')
            else:
                raise ValueError("method should be one of ['sparse_softmax', 'softmax', 'sigmoid']")
            self.loss = tfnn.reduce_mean(self.cross_entropy, name='xentropy_mean')

            if self.reg == 'l2':
                with tfnn.name_scope('l2_reg'):
                    regularizers = 0
                    for W in self.Ws:
                        regularizers += tfnn.nn.l2_loss(W, name='l2_reg')
                    regularizers *= self.l2_placeholder
                with tfnn.name_scope('l2_loss'):
                    self.loss += regularizers

            tfnn.scalar_summary('loss', self.loss)
